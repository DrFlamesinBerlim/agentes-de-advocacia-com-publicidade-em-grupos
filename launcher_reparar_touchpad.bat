@echo off
title Reparar Touchpad - Windows Optimizer

REM Verifica se ja esta rodando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando privilegios de administrador...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"
call fix_touchpad.bat
