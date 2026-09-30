@echo off
title Bootstrapping Application...
cd /d "%~dp0"
python build_exe.py
if %errorlevel% neq 0 (
    echo.
    echo Process exited with error code %errorlevel%.
)
echo.
pause
