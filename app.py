"""Portfolio Health Check: the Streamlit screen.

Every number and every piece of text about the portfolio comes from
scoring.py; this file only lays it out.
"""

import io
from html import escape

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import lookup
import rules
import scoring
from scoring import GREEN, ORANGE, RED, YELLOW

# Theme colours, shared by the CSS and the charts.
COLORS = {
    "bg": "#F7F8FA",
    "card": "#FFFFFF",
    "border": "#E3E6EB",
    "text": "#14213D",
    "text-2": "#5B6475",
    "accent": "#1F6F50",
    "yellow": "#D99A1E",
    "orange": "#D9731F",  # just over a limit: darker than yellow, lighter than red
    "red": "#C8423B",
    "neutral": "#9AA8BC",
    "note": "#6B7280",
    "light": "#CBD3DE",  # lighter step of the neutral bars
}
FONT = "Inter, 'Segoe UI', sans-serif"

STATUS_COLORS = {GREEN: COLORS["accent"], YELLOW: COLORS["yellow"], ORANGE: COLORS["orange"],
                 RED: COLORS["red"]}
BAR_COLORS = {GREEN: COLORS["neutral"], YELLOW: COLORS["yellow"], ORANGE: COLORS["orange"],
              RED: COLORS["red"]}
SLICE_COLORS = {"Equity": COLORS["text-2"], "Bonds": COLORS["neutral"], "Cash": COLORS["light"],
                "Precious metals": "#BFB39A"}  # a muted sand, apart from the status yellow
SLICE_TEXT = {"Equity": "#FFFFFF", "Bonds": COLORS["text"], "Cash": COLORS["text"],
              "Precious metals": COLORS["text"]}

PLOTLY_CONFIG = {"displayModeBar": False, "displaylogo": False}
TABS = ["Overview", "Stocks", "Charts", "Positions"]
COLUMN_LABELS = {
    "asset": "Asset",
    "value": "Value (RON)",
    "weight": "Weight",
    "sector": "Sector",
    "asset_type": "Type",
    "market_cap": "Market cap",
    "currency": "Currency",
    "region": "Region",
}
EDITOR_CONFIG = {
    "asset": st.column_config.TextColumn("Asset", help="Name or ticker, for example Apple or AAPL"),
    "value": st.column_config.NumberColumn(COLUMN_LABELS["value"], min_value=0.0, format="localized"),
    **{
        column: st.column_config.SelectboxColumn(COLUMN_LABELS[column], options=list(options))
        for column, options in scoring.EDITOR_OPTIONS.items()
    },
}
# Blank rows the editor starts with: one click on a blank row selects it, so a
# block pasted from a spreadsheet fills rows and columns (a click on the "add
# row" line would open a single cell for typing instead).
EDITOR_BLANK_ROWS = 5
NUMBER_COLUMNS = ("value", "weight")
MAX_TABLE_ROWS = 25  # longer tables scroll inside
ROW_HEIGHT = 35  # Streamlit's default row height, in pixels


# ---------------------------------------------------------------------------
# Look and feel
# ---------------------------------------------------------------------------


def inject_css() -> None:
    """The app's whole look, in a single <style> block."""
    variables = "".join(f"--{name}: {value};" for name, value in COLORS.items())
    css = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root { VARIABLES }

/* Page */
.stApp { background: var(--bg); color: var(--text); font-family: Inter, sans-serif; }
#MainMenu, footer, [data-testid="stMainMenu"], [data-testid="stToolbarActions"],
[data-testid="stAppDeployButton"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stMainBlockContainer"] { max-width: 1100px; padding: 2.5rem 1.5rem 3rem; }
[data-testid="stSidebar"] { background: var(--card); border-right: 1px solid var(--border); }
.phc-num { font-variant-numeric: tabular-nums; }

/* Header, sections, footer */
.phc-title { font-size: 1.9rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.2; }
.phc-sub { color: var(--text-2); font-size: 1.05rem; margin-top: .35rem; }
.phc-section { font-size: .78rem; font-weight: 600; letter-spacing: .06em; text-transform: uppercase;
  color: var(--text-2); margin: 1.75rem 0 .15rem; }
.phc-side-title { font-size: 1.05rem; font-weight: 600; margin-bottom: .25rem; }
.phc-footer { margin-top: 3.5rem; padding-top: 1rem; border-top: 1px solid var(--border);
  color: var(--note); font-size: .8rem; text-align: center; }

/* Cards */
.phc-card, .st-key-glance, .st-key-profile { background: var(--card); border: 1px solid var(--border);
  border-radius: 12px; padding: 1.1rem 1.25rem; }
.st-key-glance, .st-key-profile { padding: 1.25rem 1.5rem; }
.phc-grid { display: grid; gap: 1rem; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); }
.phc-grid.wide { grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); }
.phc-muted { color: var(--text-2); font-size: .9rem; line-height: 1.5; }

/* Status pill: a dot and a word */
.phc-pill { display: inline-flex; align-items: center; gap: .45rem; padding: .2rem .7rem;
  border-radius: 999px; border: 1px solid var(--border); background: var(--card);
  color: var(--text-2); font-size: .8rem; font-weight: 500; white-space: nowrap; }
.phc-dot { width: .5rem; height: .5rem; border-radius: 50%; background: var(--neutral); flex: none; }
.phc-pill.green .phc-dot { background: var(--accent); }
.phc-pill.yellow { color: var(--text); background: color-mix(in srgb, var(--yellow) 9%, white);
  border-color: color-mix(in srgb, var(--yellow) 35%, white); }
.phc-pill.yellow .phc-dot { background: var(--yellow); }
.phc-pill.red { color: var(--text); background: color-mix(in srgb, var(--red) 8%, white);
  border-color: color-mix(in srgb, var(--red) 30%, white); }
.phc-pill.red .phc-dot { background: var(--red); }
.phc-pill.orange { color: var(--text); background: color-mix(in srgb, var(--orange) 9%, white);
  border-color: color-mix(in srgb, var(--orange) 35%, white); }
.phc-pill.orange .phc-dot { background: var(--orange); }

/* Rows with a thin coloured bar on the left when they are a problem */
.phc-rows { display: flex; flex-direction: column; gap: .5rem; }
.phc-row { position: relative; display: flex; justify-content: space-between; align-items: center;
  gap: 1rem; padding: .7rem 1rem .7rem 1.1rem; background: var(--bg); border-radius: 8px; }
.phc-row.yellow::before, .phc-row.orange::before, .phc-row.red::before { content: "";
  position: absolute; left: 0; top: 7px;
  bottom: 7px; width: 3px; border-radius: 3px; }
.phc-row.yellow::before { background: var(--yellow); }
.phc-row.orange::before { background: var(--orange); }
.phc-row.red::before { background: var(--red); }
.phc-row-text { line-height: 1.4; }
.phc-row-tab { color: var(--text-2); font-size: .78rem; white-space: nowrap; }

/* At a glance */
.phc-verdict { text-align: center; font-weight: 500; line-height: 1.4; margin-top: -.5rem; }
.phc-glance-head { display: flex; align-items: center; justify-content: space-between; gap: .75rem;
  flex-wrap: wrap; margin-bottom: .75rem; }
.phc-glance-label { color: var(--text-2); font-size: .85rem; }

/* Limit cards */
.phc-limit { display: flex; flex-direction: column; gap: .55rem; }
.phc-limit-head { display: flex; justify-content: space-between; align-items: baseline; gap: .5rem; }
.phc-limit-name { font-weight: 600; }
.phc-why { position: relative; color: var(--accent); font-size: .8rem; cursor: help;
  border-bottom: 1px dotted currentColor; outline: none; }
.phc-tip { visibility: hidden; opacity: 0; position: absolute; right: 0; top: 1.5rem; width: 230px;
  z-index: 20; background: var(--text); color: #FFFFFF; font-size: .8rem; line-height: 1.45;
  padding: .6rem .75rem; border-radius: 8px; transition: opacity .15s; }
.phc-why:hover .phc-tip, .phc-why:focus .phc-tip { visibility: visible; opacity: 1; }
.phc-tip-source { display: block; margin-top: .45rem; padding-top: .45rem;
  border-top: 1px solid rgba(255, 255, 255, .2); color: #CBD3DE; }
.phc-limit-value { display: flex; align-items: baseline; gap: .5rem; flex-wrap: wrap; }
.phc-big { font-size: 2rem; font-weight: 600; letter-spacing: -0.02em; line-height: 1.1; }
.phc-of { color: var(--text-2); font-size: .9rem; }
.phc-cat { color: var(--text-2); font-size: .9rem; margin-top: -.35rem; min-height: 1.3rem; }
.phc-meter { position: relative; height: 6px; background: var(--border); border-radius: 999px; margin: .4rem 0; }
.phc-meter-fill { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 999px; background: var(--neutral); }
.phc-meter-fill.yellow { background: var(--yellow); }
.phc-meter-fill.orange { background: var(--orange); }
.phc-meter-fill.red { background: var(--red); }
.phc-meter-mark { position: absolute; top: -4px; width: 2px; height: 14px; margin-left: -1px;
  background: var(--text); border-radius: 1px; }
.phc-limit-foot { display: flex; justify-content: space-between; align-items: center;
  color: var(--text-2); font-size: .85rem; }

/* Profile */
.phc-profile-msg { margin: .75rem 0 1rem; line-height: 1.5; }
.phc-legend { display: flex; flex-direction: column; gap: .35rem; font-size: .9rem; color: var(--text-2); }
.phc-legend b { color: var(--text); font-weight: 600; }
.phc-swatch { display: inline-block; width: .7rem; height: .7rem; border-radius: 3px; margin-right: .5rem;
  vertical-align: -1px; }

/* Insights */
.phc-insight { display: flex; flex-direction: column; gap: .6rem; }
.phc-insight-head { display: flex; justify-content: space-between; align-items: center; gap: .5rem; }
.phc-insight-title { font-size: .75rem; font-weight: 600; color: var(--text-2); text-transform: uppercase;
  letter-spacing: .05em; }
.phc-insight-text { line-height: 1.45; }
.phc-insight-text .phc-why { font-size: .8rem; margin-left: .15rem; }

/* Notes, info and errors */
.phc-note { display: flex; gap: .75rem; align-items: flex-start; color: var(--note); line-height: 1.5; }
.phc-i { flex: none; width: 1.2rem; height: 1.2rem; margin-top: .1rem; border-radius: 50%;
  border: 1.5px solid var(--note); color: var(--note); font-size: .72rem; font-weight: 700;
  display: grid; place-items: center; font-family: Georgia, serif; font-style: italic; }
.phc-error { border-left: 3px solid var(--red); }
.phc-error-title { font-weight: 600; margin-bottom: .3rem; }

/* Start screen */
.phc-step { display: flex; flex-direction: column; gap: .5rem; }
.phc-step-num { width: 2rem; height: 2rem; border-radius: 50%; border: 1px solid var(--border);
  display: grid; place-items: center; font-weight: 600; color: var(--accent); }
.phc-step-title { font-weight: 600; }

/* Selected stock */
.phc-detail-name { font-weight: 600; font-size: 1.05rem; margin-bottom: .75rem; }
.phc-detail { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: .75rem; }
.phc-detail dt { color: var(--text-2); font-size: .8rem; }
.phc-detail dd { margin: .1rem 0 0; font-weight: 500; }
.phc-members { display: flex; flex-direction: column; }
.phc-member { display: flex; justify-content: space-between; gap: 1rem; padding: .4rem 0;
  border-bottom: 1px solid var(--border); }
.phc-member:last-child { border-bottom: none; }

/* Streamlit widgets. Selectors use data-testid, ARIA roles and the st-key-* classes
   Streamlit adds to keyed widgets, not its generated class names. */

/* Sample portfolios: the radio list drawn as selectable cards */
.st-key-sample [role="radiogroup"], .st-key-stress [role="radiogroup"] { gap: .5rem; }
.st-key-sample [role="radiogroup"] > div, .st-key-stress [role="radiogroup"] > div { position: relative; padding: .7rem .85rem;
  background: var(--card); border: 1px solid var(--border); border-radius: 10px;
  transition: border-color .15s, background .15s; }
.st-key-sample [role="radiogroup"] > div:hover, .st-key-stress [role="radiogroup"] > div:hover { border-color: var(--neutral); }
.st-key-sample [role="radiogroup"] > div:has(input:checked), .st-key-stress [role="radiogroup"] > div:has(input:checked) { border-color: var(--accent);
  box-shadow: inset 0 0 0 1px var(--accent); background: color-mix(in srgb, var(--accent) 4%, white); }
.st-key-sample [role="radiogroup"] > div:has(input:focus-visible), .st-key-stress [role="radiogroup"] > div:has(input:focus-visible) { outline: 2px solid var(--accent);
  outline-offset: 2px; }
.st-key-sample [data-testid="stRadioOption"], .st-key-stress [data-testid="stRadioOption"] { margin: 0; padding: 0; cursor: pointer; }
.st-key-sample [data-testid="stRadioOption"]::after, .st-key-stress [data-testid="stRadioOption"]::after { content: ""; position: absolute; inset: 0; z-index: 1; }
.st-key-sample [data-testid="stRadioOption"] div:has(+ [data-testid="stMarkdownContainer"]), .st-key-stress [data-testid="stRadioOption"] div:has(+ [data-testid="stMarkdownContainer"]) { display: none; }
.st-key-sample [data-testid="stRadioOption"] p, .st-key-stress [data-testid="stRadioOption"] p { font-weight: 600; color: var(--text); }
.st-key-sample [data-testid="stRadioCaption"], .st-key-stress [data-testid="stRadioCaption"] { margin: .15rem 0 0; padding: 0; }
.st-key-sample [data-testid="stRadioCaption"] p, .st-key-stress [data-testid="stRadioCaption"] p { font-size: .82rem; line-height: 1.4; color: var(--text-2); }

/* Upload: a card with a dotted border and our own text */
[data-testid="stFileUploaderDropzone"] { flex-direction: column; align-items: center; gap: .65rem;
  padding: 1.1rem 1rem; background: var(--card); border: 1.5px dashed var(--neutral); border-radius: 12px; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--accent); }
[data-testid="stFileUploaderDropzoneInstructions"] { order: -1; margin: 0; text-align: center; }
[data-testid="stFileUploaderDropzoneInstructions"] > * { display: none; }
[data-testid="stFileUploaderDropzoneInstructions"]::before { content: "Drop your CSV here or browse";
  color: var(--text-2); font-size: .85rem; }

/* Chart dimension: pills */
[data-testid="stButtonGroup"] [role="radiogroup"] { gap: .5rem; }
[data-testid="stButtonGroup"] button { border-radius: 999px; border: 1px solid var(--border);
  background: var(--card); color: var(--text-2); padding: .3rem 1rem; }
[data-testid="stButtonGroup"] button:hover { border-color: var(--neutral); color: var(--text); }
[data-testid="stButtonGroup"] button[aria-checked="true"] { border-color: var(--accent); color: var(--accent);
  background: color-mix(in srgb, var(--accent) 7%, white); }

/* Tabs: a thin accent line under the active tab, no backgrounds */
[role="tablist"] { gap: 1.75rem; border-bottom: 1px solid var(--border); }
[role="tab"], [role="tab"]:hover { background: transparent !important; padding: .7rem 0; }
[role="tab"] p { font-size: .95rem; font-weight: 500; color: var(--text-2); }
[role="tab"][aria-selected="true"] p, [role="tab"]:hover p { color: var(--text); }

/* Expander: same as the cards */
[data-testid="stExpander"] details { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
[data-testid="stExpander"] summary { padding: .8rem 1.1rem; font-weight: 500; color: var(--text-2); }
[data-testid="stExpander"] summary:hover { color: var(--text); }

[data-testid="stPlotlyChart"] .main-svg { background: transparent !important; }
/* A tooltip near the top or bottom bar may reach past the chart's edge. */
[data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]),
[data-testid="stPlotlyChart"] .js-plotly-plot, [data-testid="stPlotlyChart"] .main-svg {
  overflow: visible !important; }
[data-testid="stPlotlyChart"] .bglayer .bg { fill: transparent !important; }
/* Chart tooltips as small cards: a wide stroke in the card colour adds padding and
   rounds the corners, the shadows draw the edge. */
[data-testid="stPlotlyChart"] .hoverlayer .hovertext path { stroke-width: 16px !important;
  stroke-linejoin: round; filter: drop-shadow(0 0 1px rgba(20, 33, 61, .3))
  drop-shadow(0 6px 14px rgba(20, 33, 61, .12)); }
[data-testid="stPlotlyChart"] text { font-variant-numeric: tabular-nums; }
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
  background: var(--card); }
[data-testid="stDownloadButton"] button, .st-key-type_positions button { width: 100%; border-radius: 8px;
  border: 1px solid var(--accent); color: var(--accent); background: var(--card); }
[data-testid="stDownloadButton"] button:hover, .st-key-type_positions button:hover {
  background: color-mix(in srgb, var(--accent) 7%, white); color: var(--accent); border-color: var(--accent); }
.st-key-download_positions button { width: auto; }
.st-key-edit_positions button { color: var(--accent); padding: 0; }
.st-key-edit_positions button:hover { color: var(--text); }
.phc-side-gap { margin-top: 1rem; }
.phc-editor-hint { margin-bottom: .25rem; }

@media (max-width: 640px) {
  [data-testid="stMainBlockContainer"] { padding: 3.75rem 1rem 2rem; }
  .phc-title { font-size: 1.5rem; }
  .phc-row { flex-direction: column; align-items: flex-start; gap: .2rem; }
  .st-key-glance, .st-key-profile { padding: 1rem; }
}
"""
    st.html("<style>" + css.replace("VARIABLES", variables) + "</style>")


def chart_template() -> go.layout.Template:
    """One Plotly look for every chart: theme font and colours, no grid, no clutter."""
    axis = dict(
        showgrid=False,
        zeroline=False,
        showline=False,
        ticks="",
        fixedrange=True,
        automargin=True,
        ticklabelstandoff=8,
        tickfont=dict(color=COLORS["text-2"], size=12),
    )
    return go.layout.Template(
        layout=dict(
            font=dict(family=FONT, size=13, color=COLORS["text"]),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            colorway=[COLORS["neutral"]],
            showlegend=False,
            margin=dict(l=4, r=4, t=8, b=8),
            xaxis=axis,
            yaxis=axis,
            bargap=0.35,
            barcornerradius=4,
            uniformtext=dict(minsize=11, mode="hide"),
            legend=dict(font=dict(color=COLORS["text-2"], size=12), bgcolor="rgba(0,0,0,0)"),
            hoverlabel=dict(
                bgcolor=COLORS["card"],
                bordercolor=COLORS["card"],  # the CSS draws the edge and the shadow
                font=dict(family=FONT, size=13, color=COLORS["text"]),
                align="left",
                showarrow=False,
            ),
        )
    )


pio.templates["health_check"] = chart_template()
pio.templates.default = "health_check"


def show_chart(fig: go.Figure) -> None:
    st.plotly_chart(fig, theme=None, config=PLOTLY_CONFIG)


def pill(text: str, status: str = "") -> str:
    return f'<span class="phc-pill {status}"><span class="phc-dot"></span>{escape(text)}</span>'


def status_pill(status: str) -> str:
    return pill(scoring.STATUS_LABELS[status], status)


# Pill colour for each insight label (decision D5, provisional).
INSIGHT_PILLS = {"Good": GREEN, "Watch": YELLOW}


def source_tip(source: str) -> str:
    """A (?) that shows where a figure comes from, on hover or keyboard focus."""
    if not source:
        return ""
    return f' <span class="phc-why" tabindex="0">(?)<span class="phc-tip">{escape(source)}</span></span>'


def section(title: str) -> None:
    st.html(f'<div class="phc-section">{escape(title)}</div>')


def note_card(text: str) -> str:
    return f'<div class="phc-card phc-note"><span class="phc-i">i</span><span>{escape(text)}</span></div>'


def show_table(table, formats: dict, **options):
    """A table with readable headers, numbers aligned right, a very light stripe
    on every other row, and tall enough that a short table never scrolls inside."""
    stripe = f"background-color: {COLORS['bg']}"
    styled = table.style.format(formats).apply(
        lambda row: [stripe if row.name % 2 else ""] * len(row), axis=1
    )
    config = {
        column: st.column_config.Column(
            COLUMN_LABELS[column],
            alignment="right" if column in NUMBER_COLUMNS else None,
            help=" ".join(scoring.LABEL_EXPLANATIONS.values()) if column == "sector" else None,
        )
        for column in table.columns
    }
    return st.dataframe(
        styled,
        hide_index=True,
        column_config=config,
        height=ROW_HEIGHT * (min(len(table), MAX_TABLE_ROWS) + 1) + 3,
        **options,
    )


def rows_html(items: list[tuple[str, str, str]]) -> str:
    """Rows of (text, right-hand label, status); a coloured bar only for problems."""
    rows = "".join(
        f'<div class="phc-row {status}"><span class="phc-row-text phc-num">{escape(text)}</span>'
        f'<span class="phc-row-tab">{right}</span></div>'
        for text, right, status in items
    )
    return f'<div class="phc-rows">{rows}</div>'


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------


def score_ring(score: int, status: str) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            values=[score, 100 - score],
            hole=0.82,
            sort=False,
            direction="clockwise",
            marker=dict(colors=[STATUS_COLORS[status], COLORS["border"]], line=dict(width=0)),
            textinfo="none",
            hoverinfo="skip",
        )
    )
    fig.add_annotation(
        text=str(score), x=0.5, y=0.56, showarrow=False,
        font=dict(size=46, color=COLORS["text"], weight=600),
    )
    fig.add_annotation(
        text="out of 100", x=0.5, y=0.36, showarrow=False,
        font=dict(size=13, color=COLORS["text-2"]),
    )
    fig.update_layout(height=210, margin=dict(l=0, r=0, t=4, b=4))
    return fig


def asset_class_donut(slices) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            labels=slices["label"],
            values=slices["share"],
            hole=0.58,
            sort=False,
            direction="clockwise",
            marker=dict(
                colors=[SLICE_COLORS[label] for label in slices["label"]],
                line=dict(color=COLORS["card"], width=2),
            ),
            text=[scoring.fmt_pct(share) for share in slices["share"]],
            textinfo="text",
            textposition="inside",
            insidetextorientation="horizontal",
            insidetextfont=dict(color=[SLICE_TEXT[label] for label in slices["label"]], size=12),
            customdata=slices["detail"],
            hovertemplate="<b>%{label}</b><br>%{customdata}<extra></extra>",
        )
    )
    fig.update_layout(height=220, margin=dict(l=0, r=0, t=4, b=4))
    return fig


def cap_chart(shares) -> go.Figure:
    segments = [segment.capitalize() for segment in shares["segment"]]
    fig = go.Figure()
    fig.add_bar(
        name="Your stocks",
        x=segments,
        y=shares["yours"],
        marker_color=COLORS["text-2"],
        text=[scoring.fmt_pct(share) for share in shares["yours"]],
        textposition="outside",
        cliponaxis=False,
        hovertemplate="%{x}: %{text} of your stocks<extra></extra>",
    )
    top = shares["yours"].max()
    fig.update_layout(
        bargap=0.55,
        height=300,
        margin=dict(l=4, r=4, t=24, b=8),
        yaxis=dict(visible=False, range=[0, top * 1.2]),
    )
    return fig


def aligned_pcts(weights: list[float]) -> list[str]:
    """Percentages padded on the left so they line up in a tooltip: a figure space
    is as wide as a digit, a punctuation space as wide as the decimal point."""
    texts = [scoring.fmt_pct(weight) for weight in weights]
    digits = [sum(c.isdigit() for c in text) for text in texts]
    dots = [text.count(".") for text in texts]
    return [
        "\u2007" * (max(digits) - d) + "\u2008" * (max(dots) - p) + text
        for text, d, p in zip(texts, digits, dots)
    ]


def bar_hover(category: str, weight: float, phrase: str, members: list | None, shown: int = 8) -> str:
    """Tooltip of one bar: its share first, then how it stands against the limit and,
    for a sector, currency or region, the positions in it (the largest eight, then a count)."""
    muted = f'<span style="color:{COLORS["text-2"]}">'
    lines = [
        f"{muted}{escape(category)}</span>",
        f'<span style="font-size:17px"><b>{scoring.fmt_pct(weight)}</b></span>{muted} of your portfolio</span>',
    ]
    if phrase:
        lines.append(f"{muted}{phrase}</span>")
    if members:
        lines.append("")
        pcts = aligned_pcts([w for _, w in members[:shown]])
        lines += [f"{muted}{pct}</span>\u2003{escape(name)}" for pct, (name, _) in zip(pcts, members)]
        if len(members) > shown:
            lines.append(f"{muted}and {len(members) - shown} more</span>")
    return "<br>".join(lines)


# Ink for a value written on a bar, readable on the bar's colour.
TEXT_ON_BAR = {GREEN: COLORS["text"], YELLOW: COLORS["text"], ORANGE: COLORS["text"], RED: "#FFFFFF"}


def bar_chart(bars, limit: float | None, members: dict | None = None) -> go.Figure:
    top = max(bars["weight"].max(), limit or 0)
    hover = [
        bar_hover(
            row.category,
            row.weight,
            scoring.limit_phrase(row.status, row.counted, limit),
            members.get(row.category, []) if members else None,
        )
        for row in bars.itertuples()
    ]
    fig = go.Figure(
        go.Bar(
            x=bars["weight"],
            y=bars["category"],
            orientation="h",
            marker_color=[BAR_COLORS[status] for status in bars["status"]],
            text=[scoring.fmt_pct(weight) for weight in bars["weight"]],
            # Each value sits inside the end of its bar. One too small to hold it
            # (uniformtext in the template) is hidden and stays in the tooltip.
            textposition="inside",
            textangle=0,
            insidetextanchor="end",
            insidetextfont=dict(color=[TEXT_ON_BAR[status] for status in bars["status"]]),
            cliponaxis=False,
            customdata=hover,
            hovertemplate="%{customdata}<extra></extra>",
        )
    )
    fig.update_layout(
        height=70 + 30 * len(bars),
        margin=dict(l=4, r=40, t=30, b=8),
        xaxis=dict(visible=False, range=[0, top * 1.15]),
        yaxis=dict(autorange="reversed"),
    )
    if limit is not None:
        fig.add_vline(
            x=limit,
            layer="below",  # behind the bars, so it never runs through a value
            line=dict(color=COLORS["text"], width=1.5, dash="dot"),
            annotation=dict(
                text=f"Limit {scoring.fmt_pct(limit)}",
                font=dict(size=12, color=COLORS["text-2"]),
            ),
            annotation_position="top",
        )
    return fig


# ---------------------------------------------------------------------------
# Screen parts
# ---------------------------------------------------------------------------


def header() -> None:
    st.html(
        '<div class="phc-title">Portfolio Health Check</div>'
        '<div class="phc-sub">See how concentrated your portfolio is — in under a minute.</div>'
    )


def init_state() -> None:
    st.session_state.setdefault("upload_round", 0)
    st.session_state.setdefault("editing", False)
    st.session_state.setdefault("editor_round", 0)
    st.session_state.setdefault("editor_rows", scoring.empty_positions(EDITOR_BLANK_ROWS))
    st.session_state.setdefault("filled_names", [])


def clear_upload() -> None:
    """A sample was picked: drop the uploaded file by renewing the uploader's key."""
    st.session_state.upload_round += 1
    st.session_state.editing = False


def pick_sample() -> None:
    """A sample was picked: unselect the stress test and drop the uploaded file."""
    st.session_state.stress = None
    clear_upload()


def pick_stress() -> None:
    """A stress test was picked: unselect the sample and drop the uploaded file."""
    st.session_state.sample = None
    clear_upload()


def clear_sample() -> None:
    """A file was uploaded: unselect the sample and the stress test."""
    st.session_state.sample = None
    st.session_state.stress = None
    st.session_state.editing = False


def start_editing(rows=None) -> None:
    """Open the editor with the given positions, or with the last ones typed."""
    if rows is None:
        rows = st.session_state.get("editor_latest", scoring.empty_positions(EDITOR_BLANK_ROWS))
    st.session_state.sample = None
    st.session_state.stress = None
    st.session_state.upload_round += 1
    st.session_state.editing = True
    st.session_state.editor_rows = rows.reindex(columns=scoring.COLUMNS).reset_index(drop=True)
    st.session_state.editor_round += 1  # a new key gives the editor the new rows
    st.session_state.filled_names = []


def choose_portfolio():
    """Sidebar. Returns (source, id, name) of the chosen portfolio, or None."""
    samples, stress_tests = scoring.SAMPLE_PORTFOLIOS, scoring.STRESS_PORTFOLIOS
    with st.sidebar:
        st.html('<div class="phc-side-title">Sample portfolios</div>')
        sample = st.radio(
            "Sample portfolios",
            options=list(samples),
            format_func=lambda file_name: samples[file_name][0],
            captions=[description for _, description in samples.values()],
            index=None,
            key="sample",
            on_change=pick_sample,
            label_visibility="collapsed",
        )
        with st.expander("Stress tests", expanded=st.session_state.get("stress") is not None):
            stress = st.radio(
                "Stress tests",
                options=list(stress_tests),
                format_func=lambda file_name: stress_tests[file_name][0],
                captions=[description for _, description in stress_tests.values()],
                index=None,
                key="stress",
                on_change=pick_stress,
                label_visibility="collapsed",
            )
        st.html('<div class="phc-side-title phc-side-gap">Your portfolio</div>')
        upload = st.file_uploader(
            "Upload a CSV",
            type="csv",
            key=f"upload_{st.session_state.upload_round}",
            on_change=clear_sample,
        )
        st.button(
            "Type or paste positions",
            key="type_positions",
            icon=":material/edit_note:",
            on_click=start_editing,
        )
        st.download_button(
            "Download template.csv",
            data=scoring.TEMPLATE_PATH.read_bytes(),
            file_name="template.csv",
            mime="text/csv",
            icon=":material/download:",
        )

    if upload is not None:
        return io.BytesIO(upload.getvalue()), upload.file_id, upload.name
    if sample is not None:
        return scoring.DATA_DIR / sample, sample, samples[sample][0]
    if stress is not None:
        return scoring.DATA_DIR / stress, stress, stress_tests[stress][0]
    return None


def fill_summary(fills) -> str:
    """'Filled in 20 positions: 15 from SEC EDGAR, 5 from the known list.', plus the
    names that were matched to a different name, which are worth a look."""
    sources = {}
    for _, found in fills:
        sources[found.source] = sources.get(found.source, 0) + 1
    count = len(fills)
    text = f"Filled in {count} position{'s' if count > 1 else ''}: " + ", ".join(
        f"{n} from {source}" for source, n in sources.items()
    )
    renamed = [
        f"{asset} → {found.name}"
        for asset, found in fills
        if scoring.match_key(asset) != scoring.match_key(found.name)
    ]
    if renamed:
        text += ". Matched as: " + "; ".join(renamed)
    return text + ". Sector and size are approximate: check them and change anything that differs."


def edit_positions():
    """The in-app editor. Returns a validated portfolio once every row is complete."""
    section("Your positions")
    st.html(
        '<div class="phc-muted phc-editor-hint">Type a name or ticker and its value in lei: '
        "the rest fills in by itself. You can also paste rows copied from Excel or Google Sheets.</div>"
    )
    online = st.toggle(
        "Look up names online",
        value=True,
        key="online_lookup",
        help="Free, openly licensed sources: SEC EDGAR for companies listed in the US and "
        "OpenFIGI for other exchanges. Only the names you type are sent.",
    )
    edited = st.data_editor(
        st.session_state.editor_rows,
        key=f"editor_{st.session_state.editor_round}",
        num_rows="dynamic",
        hide_index=True,
        column_config=EDITOR_CONFIG,
        column_order=scoring.COLUMNS,
        placeholder="",  # empty cells stay empty instead of showing "None"
        # every row visible (header, rows and the "add row" line), like the other tables
        height=ROW_HEIGHT * (min(len(st.session_state.editor_rows), MAX_TABLE_ROWS) + 2) + 3,
    )
    find_many = lookup.find_many if online else None
    to_look_up = scoring.assets_to_look_up(edited) if online else []
    if lookup.uncached(to_look_up):
        with st.spinner("Looking up " + ", ".join(to_look_up[:3]) + ("…" if len(to_look_up) > 3 else "")):
            filled, fills, unknown = scoring.autofill(edited, find_many)
    else:
        filled, fills, unknown = scoring.autofill(edited, find_many)
    if fills:
        st.session_state.editor_rows = filled
        st.session_state.editor_round += 1
        st.session_state.filled_names = fill_summary(fills)
        st.rerun()
    st.session_state.editor_latest = edited

    rows, problems = scoring.check_editor_rows(edited)
    notes = []
    if st.session_state.filled_names:
        notes.append(st.session_state.filled_names)
    if unknown:
        notes.append("Not found: " + ", ".join(unknown) + ". Choose their details from the lists.")
    if problems:
        notes.append("To see the analysis, complete " + "; ".join(problems) + ".")
    if notes:
        st.html('<div class="phc-rows">' + "".join(note_card(n) for n in notes) + "</div>")
    st.download_button(
        "Download as CSV",
        data=scoring.to_csv(rows),
        file_name="my_portfolio.csv",
        mime="text/csv",
        icon=":material/download:",
        key="download_positions",
        disabled=rows.empty,
    )
    if rows.empty or problems:
        return None
    return scoring.validate(rows)


def offer_editor(source) -> None:
    """A CSV with names and values but missing details can be finished in the editor."""
    if not hasattr(source, "seek"):
        return
    source.seek(0)
    try:
        table = scoring.read_table(source)
    except scoring.PortfolioError:
        return
    if {"asset", "value"} <= set(table.columns):
        st.button(
            "Fill in the missing details",
            key="fill_from_csv",
            type="primary",
            icon=":material/auto_fix_high:",
            on_click=start_editing,
            args=(scoring.editor_table(table),),
        )


def error_card(message: str) -> None:
    st.html(
        '<div class="phc-card phc-error"><div class="phc-error-title">This file can\'t be analysed</div>'
        f'<div class="phc-muted">{escape(message)}</div></div>'
    )


def start_screen() -> None:
    steps = [
        (
            "Choose a portfolio",
            "Pick a sample in the side panel, upload a CSV, or type your positions.",
        ),
        ("See your score", "One number from 0 to 100, built from two concentration limits."),
        ("Read the details", "Limits, stocks, charts and every position, one tab each."),
    ]
    cards = "".join(
        f'<div class="phc-card phc-step"><span class="phc-step-num">{number}</span>'
        f'<span class="phc-step-title">{title}</span><span class="phc-muted">{text}</span></div>'
        for number, (title, text) in enumerate(steps, start=1)
    )
    section("How it works")
    st.html(f'<div class="phc-grid">{cards}</div>')


def at_a_glance(analysis: scoring.Analysis, name: str) -> None:
    section(f"At a glance · {name}")
    with st.container(key="glance"):
        left, right = st.columns([1, 1.7], gap="large", vertical_alignment="center")
        with left:
            show_chart(score_ring(analysis.score, analysis.worst_status))
            st.html(f'<div class="phc-verdict">{escape(analysis.verdict)}</div>')
        with right:
            st.html(
                '<div class="phc-glance-head"><span class="phc-glance-label">What matters most</span>'
                f"{pill(analysis.profile.name + ' profile')}</div>"
                + rows_html([(row.text, f"{escape(row.tab)} ›", row.status) for row in analysis.glance])
            )


def limit_card(result: scoring.LimitResult) -> str:
    # The bar runs to twice the limit (or to 100%), so the limit mark sits mid-way.
    scale = min(1.0, max(2 * result.limit, result.weight))
    fill = result.weight / scale * 100
    mark = result.limit / scale * 100
    category = escape(result.category) if result.category else "Funds, bonds and cash are exempt"
    bar_class = "" if result.status == GREEN else result.status
    source = f'<span class="phc-tip-source">{escape(result.source)}</span>' if result.source else ""
    return (
        '<div class="phc-card phc-limit">'
        '<div class="phc-limit-head">'
        f'<span class="phc-limit-name">{escape(result.label)}</span>'
        f'<span class="phc-why" tabindex="0">Why it matters<span class="phc-tip">{escape(result.why)}'
        f"{source}</span></span>"
        "</div>"
        '<div class="phc-limit-value">'
        f'<span class="phc-big phc-num">{scoring.fmt_pct(result.weight)}</span>'
        f'<span class="phc-of phc-num">limit {scoring.fmt_pct(result.limit)}</span>'
        "</div>"
        f'<div class="phc-cat">{category}</div>'
        f'<div class="phc-meter"><div class="phc-meter-fill {bar_class}" style="width:{fill:.1f}%"></div>'
        f'<div class="phc-meter-mark" style="left:{mark:.1f}%"></div></div>'
        '<div class="phc-limit-foot">'
        f"{status_pill(result.status)}"
        f'<span class="phc-num">Score {scoring.round_half_up(result.score)}</span>'
        "</div></div>"
    )


def overview_tab(analysis: scoring.Analysis) -> None:
    section("Concentration limits")
    st.html('<div class="phc-grid wide">' + "".join(limit_card(r) for r in analysis.limits) + "</div>")

    section("Profile")
    profile = analysis.profile
    slices = scoring.asset_class_slices(profile)
    with st.container(key="profile"):
        text, chart = st.columns([1.5, 1], gap="large", vertical_alignment="center")
        with text:
            legend = "".join(
                f'<span><span class="phc-swatch" style="background:{SLICE_COLORS[label]}"></span>'
                f'<b>{label}</b> <span class="phc-num">{scoring.fmt_pct(share)}</span>'
                f"{' · ' + escape(detail) if label == 'Equity' else ''}</span>"
                for label, share, detail in slices.itertuples(index=False)
            )
            st.html(
                pill(profile.name)
                + f'<div class="phc-profile-msg">{escape(profile.message)}</div>'
                + f'<div class="phc-legend">{legend}</div>'
            )
        with chart:
            show_chart(asset_class_donut(slices))

    section("Top insights")
    cards = "".join(
        '<div class="phc-card phc-insight"><div class="phc-insight-head">'
        f'<span class="phc-insight-title">{escape(i.title)}</span>'
        f"{pill(i.label, INSIGHT_PILLS.get(i.label, ''))}</div>"
        f'<div class="phc-insight-text phc-num">{escape(i.text)}{source_tip(i.source)}</div></div>'
        for i in analysis.insights
    )
    st.html(f'<div class="phc-grid">{cards}</div>')

    section("Warnings")
    warnings = [(w.text, status_pill(w.status), w.status) for w in analysis.warnings]
    if not warnings:
        st.html('<div class="phc-card phc-muted">No warnings: every limit is below its yellow threshold.</div>')
        return
    st.html(rows_html(warnings[:3]))
    if len(warnings) > 3:
        with st.expander("See all warnings"):
            st.html(rows_html(warnings[3:]))


def stocks_tab(analysis: scoring.Analysis, portfolio_id: str) -> None:
    table = scoring.stocks_table(analysis)
    if table.empty:
        st.html(note_card("This portfolio holds no individual stocks, so there is no market-cap breakdown."))
        return

    section("Market cap of your stocks")
    show_chart(cap_chart(scoring.cap_shares(analysis)))
    notes = [n for n in analysis.notes if n.tab == "Stocks"]
    if notes:
        st.html('<div class="phc-rows">' + "".join(note_card(n.text) for n in notes) + "</div>")

    section("Your stocks")
    st.html('<div class="phc-muted">Select a row to see the details of a stock.</div>')
    event = show_table(
        table,
        {"weight": scoring.fmt_pct},
        on_select="rerun",
        selection_mode="single-row",
        key=f"stocks_{portfolio_id}",  # a new portfolio starts with no selection
    )
    if event.selection.rows:
        stock = table.iloc[event.selection.rows[0]]
        details = [
            ("Sector", stock["sector"]),
            ("Market cap", stock["market_cap"]),
            ("Region", stock.get("region", "–")),
            ("Weight", scoring.fmt_pct(stock["weight"])),
        ]
        items = "".join(f"<div><dt>{label}</dt><dd>{escape(str(value))}</dd></div>" for label, value in details)
        st.html(
            f'<div class="phc-card"><div class="phc-detail-name">{escape(stock["asset"])}</div>'
            f'<dl class="phc-detail">{items}</dl></div>'
        )


def members_card(category: str, share: float, members: list[tuple[str, float]]) -> str:
    rows = "".join(
        f'<div class="phc-member"><span>{escape(name)}</span>'
        f'<span class="phc-num">{scoring.fmt_pct(weight)}</span></div>'
        for name, weight in members
    )
    return (
        f'<div class="phc-card"><div class="phc-detail-name">{escape(category)} · '
        f'{scoring.fmt_pct(share)} of your portfolio</div><div class="phc-members">{rows}</div></div>'
    )


def charts_tab(analysis: scoring.Analysis, portfolio_id: str) -> None:
    dimensions = scoring.chart_dimensions(analysis)
    dimension = st.pills(
        "Dimension",
        options=list(dimensions),
        format_func=dimensions.get,
        default="sector",
        required=True,
        key=f"dimension_{len(dimensions)}",
        label_visibility="collapsed",
    )
    bars, limit = scoring.chart_data(analysis, dimension)
    # Each bar of Sector, Currency and Region holds several positions: show them.
    members = scoring.bar_members(analysis, dimension) if dimension != "asset" else None
    event = st.plotly_chart(
        bar_chart(bars, limit, members),
        theme=None,
        config=PLOTLY_CONFIG,
        on_select="rerun" if members else "ignore",
        selection_mode="points",
        key=f"chart_{portfolio_id}_{dimension}",  # a new portfolio starts with no bar picked
    )
    points = event.selection.points if members else []
    if points:
        category = points[0]["y"]
        share = float(bars.loc[bars["category"] == category, "weight"].iloc[0])
        st.html(members_card(category, share, members[category]))
    elif members:
        st.html('<div class="phc-muted">Hover over a bar to see the positions in it, or click it to list them.</div>')
    explanations = scoring.label_explanations(bars["category"]) if dimension == "sector" else []
    if explanations:
        st.html(note_card(" ".join(explanations) + " They don't count towards the sector limit, so they stay grey."))
    elif dimension in ("sector", "asset"):
        st.html('<div class="phc-muted">Broad ETFs, bonds and cash are exempt from this limit and stay grey.</div>')
    for note in analysis.notes:
        if note.key == dimension:  # the region and currency notes sit under their charts
            st.html(note_card(note.text))


def positions_tab(analysis: scoring.Analysis) -> None:
    columns = [c for c in COLUMN_LABELS if c in analysis.positions.columns]
    show_table(analysis.positions[columns], {"value": scoring.fmt_ron, "weight": scoring.fmt_pct})


@st.dialog("Before you start", width="large", dismissible=False)
def about_dialog() -> None:
    """What the app is and how the score is calculated: once per visit, and from the footer."""
    sector, asset = rules.LIMITS["sector"], rules.LIMITS["asset"]
    pct = scoring.fmt_pct
    # What is said about funds depends on whether index figures are installed (D6, D8).
    if scoring.index_funds().empty:
        narrow = ""
        inside = "It does not look inside funds: a broad fund counts as diversified."
    else:
        narrow = (" A fund on a narrower index, like the Nasdaq-100, counts towards the sector"
                  " limit by what it holds.")
        inside = ("Funds are counted as copies of their index, and only the largest companies"
                  " of each index are known.")
    st.markdown(
        f"""
**Just math, not investment advice.** Portfolio Health Check shows how concentrated a portfolio
is, using only the numbers you enter. It does not recommend buying, selling or holding anything,
and it does not know your goals, income or situation.

**How the score is calculated**
- Each position's weight is its value divided by the total of the portfolio.
- Two limits look at the largest share: one sector (full score below {pct(sector["yellow_from"])},
  limit {pct(sector["limit"])}) and one single position (full score below
  {pct(asset["yellow_from"])}, limit {pct(asset["limit"])}).
- Each limit scores from 20 to 100, and the score is the average of the two.
- Broad funds, government bonds, cash and precious metals don't count towards the limits, but
  they are part of the total. A broad fund already spreads your money over hundreds of
  companies, so it doesn't lower your score.
- A corporate bond counts like a position in the company.{narrow}
- The limits are the ones EU and US law set for funds, used here as a reference. The Watch
  thresholds and the sector margin are example values.

**What it can't see**
- {inside}
- Details looked up online come from public sources and may be wrong: check them.

**Your data**
- The app runs on your computer and keeps your portfolio only in its memory: nothing is written
  to a file, and it is gone when you close the app.
- To keep positions you typed, use "Download as CSV": the file is saved where you choose.
- If online lookup is on, only the names and tickers you type are sent to SEC EDGAR and OpenFIGI,
  never the values. You can turn the lookup off.
- The app collects no usage statistics.
"""
    )
    if st.button("I understand", type="primary"):
        st.session_state.understood = True
        st.rerun()


def footer() -> None:
    if st.button("How the score works", key="about", type="tertiary", icon=":material/info:"):
        about_dialog()
    st.html(
        '<div class="phc-footer">Analysis, not investment advice. '
        "Both limits follow EU and US fund rules; the Watch thresholds and the sector "
        "margin are examples until replaced with the author's thesis rules.</div>"
    )


def main() -> None:
    st.set_page_config(
        page_title="Portfolio Health Check",
        page_icon=":material/donut_large:",
        layout="wide",
    )
    inject_css()
    init_state()
    header()
    if not st.session_state.get("understood"):
        about_dialog()

    chosen = choose_portfolio()
    portfolio = None
    if st.session_state.editing:
        portfolio = edit_positions()
        portfolio_id, name = f"editor_{st.session_state.editor_round}", "Your positions"
    elif chosen is not None:
        source, portfolio_id, name = chosen
        try:
            portfolio = scoring.load_portfolio(source)
        except scoring.PortfolioError as error:
            error_card(str(error))
            offer_editor(source)
    if portfolio is None:
        if not st.session_state.editing:
            start_screen()
        footer()
        return

    analysis = scoring.analyze(portfolio)
    for message in analysis.info:
        st.html(note_card(message))

    at_a_glance(analysis, name)
    if not st.session_state.editing:
        st.button(
            "Edit these positions",
            key="edit_positions",
            type="tertiary",
            icon=":material/edit:",
            on_click=start_editing,
            args=(portfolio,),
        )
    overview, stocks, charts, positions = st.tabs(TABS)
    with overview:
        overview_tab(analysis)
    with stocks:
        stocks_tab(analysis, portfolio_id)
    with charts:
        charts_tab(analysis, portfolio_id)
    with positions:
        positions_tab(analysis)
    footer()


main()
