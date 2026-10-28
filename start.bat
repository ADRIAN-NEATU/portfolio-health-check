@echo off
rem Portfolio Health Check: double-click this file to start the app on Windows.
rem The first run creates .venv and installs the packages (needs Python 3.10+).
cd /d "%~dp0"
title Portfolio Health Check

if not exist ".venv\Scripts\python.exe" (
    echo First run: setting up the app, this takes a minute...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    if not exist ".venv\Scripts\python.exe" (
        echo.
        echo Python 3.10 or newer is needed. Install it from https://www.python.org/downloads/
        echo and tick "Add python.exe to PATH", then double-click this file again.
        pause
        exit /b 1
    )
    ".venv\Scripts\python.exe" -m pip install --disable-pip-version-check -q -r requirements.txt
)

rem Skip Streamlit's one-time e-mail question (the same as pressing Enter).
if not exist "%USERPROFILE%\.streamlit\credentials.toml" (
    if not exist "%USERPROFILE%\.streamlit" mkdir "%USERPROFILE%\.streamlit"
    > "%USERPROFILE%\.streamlit\credentials.toml" (
        echo [general]
        echo email = ""
    )
)

echo Starting Portfolio Health Check at http://localhost:8501
echo Keep this window open while you use the app; close it to stop the app.
".venv\Scripts\python.exe" -m streamlit run app.py
pause