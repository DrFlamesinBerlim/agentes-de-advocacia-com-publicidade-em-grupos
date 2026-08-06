@echo off
title Limpar Sistema - PREVIA (Nada e deletado)

REM Verifica se ja esta rodando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando privilegios de administrador...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

where python >nul 2>&1
if %errorlevel% equ 0 (
    python system_cleaner_advanced.py
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        py system_cleaner_advanced.py
    ) else (
        color 0C
        echo.
        echo [ERRO] Python nao foi encontrado neste computador.
        echo.
        echo Baixe e instale em: https://www.python.org/downloads/
        echo Marque a opcao "Add Python to PATH" durante a instalacao.
        echo.
    )
)

echo.
echo ================================================================================
echo Pressione qualquer tecla para fechar esta janela...
pause >nul
