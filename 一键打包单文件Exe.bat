@echo off
title Packaging Gacha Tracker Desktop App...
cd /d "%~dp0"
python build_exe.py
if %errorlevel% neq 0 (
    echo.
    echo Packaging encountered an error. Please check the log above.
)
echo.
pause
