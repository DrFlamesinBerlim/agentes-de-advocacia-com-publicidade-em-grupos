@echo off
title Otimizador Rapido - Alivia a Maquina
setlocal enabledelayedexpansion

REM ============================================================
REM  Auto-elevacao: se nao for admin, reabre pedindo permissao
REM ============================================================
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Solicitando permissao de administrador...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
    exit /b
)

cls
color 0B
echo ================================================================================
echo.
echo                 OTIMIZADOR RAPIDO - ALIVIANDO A MAQUINA
echo.
echo   Seguro: cria ponto de restauracao e NAO mexe em
echo   criptografia, rede, audio, touchpad ou seguranca.
echo.
echo ================================================================================
echo.

REM ---- Estado ANTES ----
echo [MEDINDO ESTADO INICIAL]
for /f %%A in ('powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)"') do set RAM_ANTES=%%A
for /f %%D in ('powershell -NoProfile -Command "[math]::Round((Get-PSDrive C).Free/1MB)"') do set DISCO_ANTES=%%D
echo    RAM livre no inicio:   aproximadamente !RAM_ANTES! MB
echo    Disco C: livre agora:  aproximadamente !DISCO_ANTES! MB
echo.

REM ============================================================
REM  PASSO 1 - Ponto de restauracao (seguranca)
REM ============================================================
echo ================================================================================
echo PASSO 1/6: Criando ponto de restauracao...
echo ================================================================================
powershell -NoProfile -Command "Checkpoint-Computer -Description 'Otimizacao Rapida' -RestorePointType 'MODIFY_SETTINGS'" >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] Ponto de restauracao criado
) else (
    echo    [AVISO] Nao foi possivel criar ponto ^(continua mesmo assim^)
)
echo.

REM ============================================================
REM  PASSO 2 - Limpar arquivos temporarios
REM ============================================================
echo ================================================================================
echo PASSO 2/6: Limpando arquivos temporarios...
echo ================================================================================
echo    Limpando pasta Temp do usuario...
del /f /s /q "%TEMP%\*" >nul 2>&1
echo    Limpando Temp do Windows...
del /f /s /q "%SystemRoot%\Temp\*" >nul 2>&1
echo    Limpando Prefetch...
del /f /s /q "%SystemRoot%\Prefetch\*" >nul 2>&1
echo    [OK] Temporarios limpos
echo.

REM ============================================================
REM  PASSO 3 - Esvaziar a Lixeira
REM ============================================================
echo ================================================================================
echo PASSO 3/6: Esvaziando a Lixeira...
echo ================================================================================
powershell -NoProfile -Command "Clear-RecycleBin -Force -ErrorAction SilentlyContinue" >nul 2>&1
echo    [OK] Lixeira esvaziada
echo.

REM ============================================================
REM  PASSO 4 - Limpar cache do Windows Update
REM ============================================================
echo ================================================================================
echo PASSO 4/6: Limpando cache do Windows Update...
echo ================================================================================
net stop wuauserv >nul 2>&1
del /f /s /q "%SystemRoot%\SoftwareDistribution\Download\*" >nul 2>&1
net start wuauserv >nul 2>&1
echo    [OK] Cache do Windows Update limpo
echo.

REM ============================================================
REM  PASSO 5 - Limpar cache de DNS
REM ============================================================
echo ================================================================================
echo PASSO 5/6: Limpando cache de DNS...
echo ================================================================================
ipconfig /flushdns >nul 2>&1
echo    [OK] DNS limpo
echo.

REM ============================================================
REM  PASSO 6 - Desligar SOMENTE telemetria (100%% seguro)
REM ============================================================
echo ================================================================================
echo PASSO 6/6: Desligando telemetria ^(coleta de dados^)...
echo ================================================================================
echo    Desligando DiagTrack ^(telemetria^)...
sc stop DiagTrack >nul 2>&1
sc config DiagTrack start= disabled >nul 2>&1
echo    Desligando dmwappushservice ^(publicidade^)...
sc stop dmwappushservice >nul 2>&1
sc config dmwappushservice start= disabled >nul 2>&1
echo    [OK] Telemetria desligada
echo.

REM ---- Estado DEPOIS ----
echo ================================================================================
echo                            RESULTADO
echo ================================================================================
for /f %%A in ('powershell -NoProfile -Command "[math]::Round((Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory/1024)"') do set RAM_DEPOIS=%%A
for /f %%D in ('powershell -NoProfile -Command "[math]::Round((Get-PSDrive C).Free/1MB)"') do set DISCO_DEPOIS=%%D
set /a DISCO_LIBERADO=DISCO_DEPOIS-DISCO_ANTES
echo    ---------------------------------------------------------
echo    DISCO C: liberado:  aproximadamente !DISCO_LIBERADO! MB
echo    ---------------------------------------------------------
echo    RAM livre antes:  aproximadamente !RAM_ANTES! MB
echo    RAM livre depois: aproximadamente !RAM_DEPOIS! MB
echo.
color 0A
echo   [CONCLUIDO] Maquina aliviada com sucesso!
echo.
echo   DICA: para ganhar ainda mais velocidade, aperte
echo   Ctrl+Shift+Esc, va na aba INICIALIZAR e desabilite
echo   os programas que voce nao usa ^(Spotify, Discord, etc^).
echo.
echo   Reinicie o notebook quando puder para completar.
echo ================================================================================
echo.
pause
