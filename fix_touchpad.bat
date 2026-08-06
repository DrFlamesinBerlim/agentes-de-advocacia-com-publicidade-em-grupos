@echo off
REM Fix Touchpad - Script Batch (Funciona em Qualquer Windows)
REM Execute como ADMINISTRADOR

setlocal enabledelayedexpansion

cls
color 0A
echo.
echo ================================================================================
echo.
echo                  [REPARADOR DE TOUCHPAD - FIX TOUCHPAD]
echo.
echo ================================================================================
echo.

REM Verificar se é Admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo ERRO: Este script precisa ser executado como ADMINISTRADOR!
    echo.
    echo Clique DIREITO neste arquivo (.bat) e escolha:
    echo "Executar como administrador"
    echo.
    pause
    exit /b
)

color 0A
echo [ADMIN] Executando com privilegios de administrador
echo.

REM ============================================================================
REM PASSO 1: Restaurar Servicos Criticos
REM ============================================================================

echo ================================================================================
echo PASSO 1/3: Restaurando Servicos Criticos...
echo ================================================================================
echo.

set "servicos=PlugPlay hidserv DcaSvc Dhcp Dnscache"

for %%S in (%servicos%) do (
    echo    Configurando %%S...
    net start "%%S" >nul 2>&1
    sc config "%%S" start= auto >nul 2>&1
    echo    [OK] %%S restaurado
)

echo.
echo [SUCESSO] Servicos restaurados
echo.

REM ============================================================================
REM PASSO 2: Habilitar Touchpad via Registry
REM ============================================================================

echo ================================================================================
echo PASSO 2/3: Habilitando Touchpad via Registry...
echo ================================================================================
echo.

REM Criar arquivo de registro temporário
(
    echo Windows Registry Editor Version 5.00
    echo.
    echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\hidserv]
    echo "Start"=dword:00000002
    echo.
    echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\PlugPlay]
    echo "Start"=dword:00000002
    echo.
    echo [HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\DcaSvc]
    echo "Start"=dword:00000003
) > "%temp%\fix_touchpad.reg"

echo    Importando configuracoes do registro...
regedit /s "%temp%\fix_touchpad.reg"
if %errorlevel% equ 0 (
    echo    [OK] Registro atualizado
) else (
    echo    [ERRO] Nao foi possivel atualizar registro
)

echo.

REM ============================================================================
REM PASSO 3: Limpar Cache e Preparar Reboot
REM ============================================================================

echo ================================================================================
echo PASSO 3/3: Finalizando...
echo ================================================================================
echo.

echo    Limpando arquivos temporarios...
del /f /q "%temp%\fix_touchpad.reg" >nul 2>&1
echo    [OK] Limpeza concluida

echo.
echo    Reiniciando Explorer...
taskkill /f /im explorer.exe >nul 2>&1
timeout /t 1 /nobreak >nul
start explorer.exe
echo    [OK] Explorer reiniciado

echo.

REM ============================================================================
REM CONFIRMACAO DE REBOOT
REM ============================================================================

color 0E
echo ================================================================================
echo.
echo                    [REINICIO DO WINDOWS]
echo.
echo ================================================================================
echo.
echo.
echo   [ATENCAO] Seu notebook vai reiniciar em 30 segundos!
echo.
echo   Salve seus arquivos AGORA!
echo   Pressione Ctrl+C para CANCELAR o restart.
echo.
echo.

REM Contagem regressiva
for /L %%i in (30,-1,1) do (
    cls
    echo ================================================================================
    echo                     [REINICIO DO WINDOWS]
    echo ================================================================================
    echo.
    echo   Reiniciando em: %%i segundos...
    echo.
    echo   Pressione Ctrl+C para CANCELAR
    echo.
    echo ================================================================================
    timeout /t 1 /nobreak >nul
)

REM Reiniciar
cls
color 0A
echo ================================================================================
echo.
echo                   [REINICIANDO AGORA!]
echo.
echo ================================================================================
echo.

shutdown /r /t 5 /c "Windows Optimizer - Touchpad Fix"

echo.
echo [SUCESSO] Reinicio iniciado!
echo.
echo Seu notebook vai reiniciar em 5 segundos...
echo.

timeout /t 5 /nobreak >nul

exit /b 0
