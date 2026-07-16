@echo off
title Limpar Sistema - APLICANDO MUDANCAS

REM Verifica se ja esta rodando como administrador
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando privilegios de administrador...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cd /d "%~dp0"

color 0E
echo ================================================================================
echo   ATENCAO: Este modo REALMENTE DELETA arquivos temporarios e de cache.
echo   Um restore point sera criado automaticamente antes de qualquer mudanca.
echo ================================================================================
echo.
set /p CONFIRMA="Digite SIM para continuar ou qualquer outra tecla para cancelar: "
if /i not "%CONFIRMA%"=="SIM" (
    echo.
    echo Operacao cancelada. Nada foi alterado.
    echo.
    pause
    exit /b
)

color 0A

where python >nul 2>&1
if %errorlevel% equ 0 (
    python system_cleaner_advanced.py --apply
) else (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        py system_cleaner_advanced.py --apply
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
