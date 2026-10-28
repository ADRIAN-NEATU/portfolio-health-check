"""Portfolio Health Check: the Streamlit screen.

Every number and every piece of text about the portfolio comes from
scoring.py; this file only lays it out.
"""

import io
from html import escape

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

import scoring
from scoring import GREEN, RED, YELLOW

# Theme colours, shared by the CSS and the charts.
COLORS = {
    "bg": "#F7F8FA",
    "card": "#FFFFFF",
    "border": "#E3E6EB",
    "text": "#14213D",
    "text-2": "#5B6475",
    "accent": "#1F6F50",
    "yellow": "#D99A1E",
    "red": "#C8423B",
    "neutral": "#9AA8BC",
    "note": "#6B7280",
    "light": "#CBD3DE",  # lighter step of the neutral bars
}
FONT = "Inter, 'Segoe UI', sans-serif"

STATUS_COLORS = {GREEN: COLORS["accent"], YELLOW: COLORS["yellow"], RED: COLORS["red"]}
BAR_COLORS = {GREEN: COLORS["neutral"], YELLOW: COLORS["yellow"], RED: COLORS["red"]}
SLICE_COLORS = {"Equity": COLORS["text-2"], "Bonds": COLORS["neutral"], "Cash": COLORS["light"]}
SLICE_TEXT = {"Equity": "#FFFFFF", "Bonds": COLORS["text"], "Cash": COLORS["text"]}

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

/* Rows with a thin coloured bar on the left when they are a problem */
.phc-rows { display: flex; flex-direction: column; gap: .5rem; }
.phc-row { position: relative; display: flex; justify-content: space-between; align-items: center;
  gap: 1rem; padding: .7rem 1rem .7rem 1.1rem; background: var(--bg); border-radius: 8px; }
.phc-row.yellow::before, .phc-row.red::before { content: ""; position: absolute; left: 0; top: 7px;
  bottom: 7px; width: 3px; border-radius: 3px; }
.phc-row.yellow::before { background: var(--yellow); }
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
.phc-limit-value { display: flex; align-items: baseline; gap: .5rem; flex-wrap: wrap; }
.phc-big { font-size: 2rem; font-weight: 600; letter-spacing: -0.02em; line-height: 1.1; }
.phc-of { color: var(--text-2); font-size: .9rem; }
.phc-cat { color: var(--text-2); font-size: .9rem; margin-top: -.35rem; min-height: 1.3rem; }
.phc-meter { position: relative; height: 6px; background: var(--border); border-radius: 999px; margin: .4rem 0; }
.phc-meter-fill { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 999px; background: var(--neutral); }
.phc-meter-fill.yellow { background: var(--yellow); }
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

/* Streamlit widgets */
.stTabs [data-baseweb="tab-list"] { gap: 1.75rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] { padding: .7rem 0; }
.stTabs [data-baseweb="tab"] p { font-size: .95rem; font-weight: 500; color: var(--text-2); }
.stTabs [aria-selected="true"] p { color: var(--text); }
[data-testid="stPlotlyChart"] .main-svg { background: transparent !important; }
[data-testid="stPlotlyChart"] .bglayer .bg { fill: transparent !important; }
[data-testid="stExpander"] details { background: var(--card); border: 1px solid var(--border); border-radius: 12px; }
[data-testid="stDataFrame"] { border: 1px solid var(--border); border-radius: 12px; overflow: hidden;
  background: var(--card); }
[data-testid="stFileUploaderDropzone"] { background: var(--bg); border: 1px dashed var(--border); border-radius: 12px; }
[data-testid="stDownloadButton"] button { width: 100%; border-radius: 8px; border: 1px solid var(--accent);
  color: var(--accent); background: var(--card); }
[data-testid="stDownloadButton"] button:hover { background: color-mix(in srgb, var(--accent) 7%, white);
  color: var(--accent); border-color: var(--accent); }

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
                bordercolor=COLORS["border"],
                font=dict(family=FONT, size=12, color=COLORS["text"]),
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


def section(title: str) -> None:
    st.html(f'<div class="phc-section">{escape(title)}</div>')


def note_card(text: str) -> str:
    return f'<div class="phc-card phc-note"><span class="phc-i">i</span><span>{escape(text)}</span></div>'


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


def cap_chart(comparison) -> go.Figure:
    segments = [segment.capitalize() for segment in comparison["segment"]]
    fig = go.Figure()
    for name, column, color in [
        ("Your stocks", "yours", COLORS["text-2"]),
        ("US market (approx.)", "market", COLORS["neutral"]),
    ]:
        fig.add_bar(
            name=name,
            x=segments,
            y=comparison[column],
            marker_color=color,
            text=[scoring.fmt_pct(share) for share in comparison[column]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate=f"{name}<br>%{{x}}: %{{text}}<extra></extra>",
        )
    top = max(comparison["yours"].max(), comparison["market"].max())
    fig.update_layout(
        barmode="group",
        bargap=0.55,
        bargroupgap=0.12,
        height=300,
        showlegend=True,
        legend=dict(orientation="h", x=0, y=1.14),
        margin=dict(l=4, r=4, t=40, b=8),
        yaxis=dict(visible=False, range=[0, top * 1.2]),
    )
    return fig


def bar_chart(bars, limit: float | None) -> go.Figure:
    fig = go.Figure(
        go.Bar(
            x=bars["weight"],
            y=bars["category"],
            orientation="h",
            marker_color=[BAR_COLORS[status] for status in bars["status"]],
            text=[scoring.fmt_pct(weight) for weight in bars["weight"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}: %{text}<extra></extra>",
        )
    )
    top = max(bars["weight"].max(), limit or 0)
    fig.update_layout(
        height=70 + 30 * len(bars),
        margin=dict(l=4, r=40, t=30, b=8),
        xaxis=dict(visible=False, range=[0, top * 1.15]),
        yaxis=dict(autorange="reversed"),
    )
    if limit is not None:
        fig.add_vline(
            x=limit,
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


def clear_upload() -> None:
    """A sample was picked: drop the uploaded file by renewing the uploader's key."""
    st.session_state.upload_round += 1


def clear_sample() -> None:
    """A file was uploaded: unselect the sample."""
    st.session_state.sample = None


def choose_portfolio():
    """Sidebar. Returns (source, id, name) of the chosen portfolio, or None."""
    st.session_state.setdefault("upload_round", 0)
    samples = scoring.SAMPLE_PORTFOLIOS
    with st.sidebar:
        st.html('<div class="phc-side-title">Portfolio</div>')
        sample = st.radio(
            "Sample portfolios",
            options=list(samples),
            format_func=lambda file_name: samples[file_name][0],
            captions=[description for _, description in samples.values()],
            index=None,
            key="sample",
            on_change=clear_upload,
        )
        upload = st.file_uploader(
            "Or upload your own CSV",
            type="csv",
            key=f"upload_{st.session_state.upload_round}",
            on_change=clear_sample,
        )
        st.download_button(
            "Download template.csv",
            data=scoring.TEMPLATE_PATH.read_bytes(),
            file_name="template.csv",
            mime="text/csv",
        )

    if upload is not None:
        return io.BytesIO(upload.getvalue()), upload.file_id, upload.name
    if sample is not None:
        return scoring.DATA_DIR / sample, sample, samples[sample][0]
    return None


def error_card(message: str) -> None:
    st.html(
        '<div class="phc-card phc-error"><div class="phc-error-title">This file can\'t be analysed</div>'
        f'<div class="phc-muted">{escape(message)}</div></div>'
    )


def start_screen() -> None:
    steps = [
        ("Choose a portfolio", "Pick one of the samples in the side panel, or upload your own CSV."),
        ("See your score", "One number from 0 to 100, built from three concentration limits."),
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
    return (
        '<div class="phc-card phc-limit">'
        '<div class="phc-limit-head">'
        f'<span class="phc-limit-name">{escape(result.label)}</span>'
        f'<span class="phc-why" tabindex="0">Why it matters<span class="phc-tip">{escape(result.why)}</span></span>'
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
        f'{pill(i.label, YELLOW if i.label == "Watch" else "")}</div>'
        f'<div class="phc-insight-text phc-num">{escape(i.text)}</div></div>'
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
    show_chart(cap_chart(scoring.cap_comparison(analysis)))
    notes = [n for n in analysis.notes if n.tab == "Stocks"]
    if notes:
        st.html('<div class="phc-rows">' + "".join(note_card(n.text) for n in notes) + "</div>")

    section("Your stocks")
    st.html('<div class="phc-muted">Select a row to see the details of a stock.</div>')
    event = st.dataframe(
        table.style.format({"weight": scoring.fmt_pct}),
        hide_index=True,
        column_config=COLUMN_LABELS,
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


def charts_tab(analysis: scoring.Analysis) -> None:
    dimensions = scoring.chart_dimensions(analysis)
    dimension = st.segmented_control(
        "Dimension",
        options=list(dimensions),
        format_func=dimensions.get,
        default="sector",
        required=True,
        key=f"dimension_{len(dimensions)}",
        label_visibility="collapsed",
    )
    bars, limit = scoring.chart_data(analysis, dimension)
    show_chart(bar_chart(bars, limit))
    if dimension in ("sector", "asset"):
        st.html('<div class="phc-muted">Broad ETFs, bonds and cash are exempt from this limit and stay grey.</div>')
    if dimension == "region":
        for note in analysis.notes:
            if note.key == "region":
                st.html(note_card(note.text))


def positions_tab(analysis: scoring.Analysis) -> None:
    st.dataframe(
        analysis.positions.style.format({"value": scoring.fmt_ron, "weight": scoring.fmt_pct}),
        hide_index=True,
        column_config=COLUMN_LABELS,
        column_order=[c for c in COLUMN_LABELS if c in analysis.positions.columns],
    )


def footer() -> None:
    st.html(
        '<div class="phc-footer">Analysis, not investment advice. '
        "Thresholds are examples until replaced with the author's thesis rules.</div>"
    )


def main() -> None:
    st.set_page_config(
        page_title="Portfolio Health Check",
        page_icon=":material/donut_large:",
        layout="wide",
    )
    inject_css()
    header()

    chosen = choose_portfolio()
    portfolio = None
    if chosen is not None:
        source, portfolio_id, name = chosen
        try:
            portfolio = scoring.load_portfolio(source)
        except scoring.PortfolioError as error:
            error_card(str(error))
    if portfolio is None:
        start_screen()
        footer()
        return

    analysis = scoring.analyze(portfolio)
    for message in analysis.info:
        st.html(note_card(message))

    at_a_glance(analysis, name)
    overview, stocks, charts, positions = st.tabs(TABS)
    with overview:
        overview_tab(analysis)
    with stocks:
        stocks_tab(analysis, portfolio_id)
    with charts:
        charts_tab(analysis)
    with positions:
        positions_tab(analysis)
    footer()


main()
