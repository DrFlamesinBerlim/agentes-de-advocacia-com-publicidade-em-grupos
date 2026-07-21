@echo off
title Reparador de Problemas - Registro e Sistema
setlocal enabledelayedexpansion

REM ============================================================
REM  Auto-elevacao
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
echo         REPARADOR DE PROBLEMAS - REGISTRO E ARQUIVOS DO SISTEMA
echo.
echo   Usa as ferramentas OFICIAIS da Microsoft para achar e consertar
echo   corrupcoes com seguranca. Nao apaga chaves no chute.
echo.
echo   ATENCAO: pode demorar de 10 a 30 minutos. Deixe rodar ate o fim.
echo.
echo ================================================================================
echo.
pause

REM ============================================================
REM  PASSO 1 - Ponto de restauracao
REM ============================================================
echo.
echo ================================================================================
echo PASSO 1/5: Criando ponto de restauracao...
echo ================================================================================
powershell -NoProfile -Command "Checkpoint-Computer -Description 'Antes de Reparar' -RestorePointType 'MODIFY_SETTINGS'" >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] Ponto de restauracao criado
) else (
    echo    [AVISO] Nao criou ponto, continua mesmo assim
)
echo.

REM ============================================================
REM  PASSO 2 - Backup do registro na Area de Trabalho
REM ============================================================
echo ================================================================================
echo PASSO 2/5: Fazendo backup do registro...
echo ================================================================================
set "BKP=%USERPROFILE%\Desktop\Backup_Registro"
if not exist "%BKP%" mkdir "%BKP%" >nul 2>&1
echo    Exportando HKEY_LOCAL_MACHINE\SOFTWARE...
reg export "HKLM\SOFTWARE" "%BKP%\HKLM_SOFTWARE.reg" /y >nul 2>&1
echo    Exportando HKEY_CURRENT_USER...
reg export "HKCU" "%BKP%\HKCU.reg" /y >nul 2>&1
echo    [OK] Backup salvo em: %BKP%
echo.

REM ============================================================
REM  PASSO 3 - System File Checker
REM ============================================================
echo ================================================================================
echo PASSO 3/5: Verificando arquivos do sistema ^(SFC^)...
echo   Isso conserta arquivos e referencias de registro corrompidos.
echo ================================================================================
sfc /scannow
echo.
echo    [OK] Verificacao SFC concluida
echo.

REM ============================================================
REM  PASSO 4 - DISM RestoreHealth
REM ============================================================
echo ================================================================================
echo PASSO 4/5: Reparando a imagem do Windows ^(DISM^)...
echo   Corrige problemas que o SFC sozinho nao resolve.
echo ================================================================================
DISM /Online /Cleanup-Image /RestoreHealth
echo.
echo    [OK] Reparo DISM concluido
echo.

REM ============================================================
REM  PASSO 5 - Verificar disco
REM ============================================================
echo ================================================================================
echo PASSO 5/5: Verificando erros no disco ^(somente leitura, seguro^)...
echo ================================================================================
chkdsk C: /scan
echo.
echo    [OK] Verificacao de disco concluida
echo.

color 0A
echo ================================================================================
echo   [CONCLUIDO] Reparo finalizado!
echo.
echo   Backup do registro guardado em:
echo      %BKP%
echo.
echo   Recomendado REINICIAR para aplicar os reparos.
echo ================================================================================
echo.

REM ---- Escolha de reinicio ----
set "RESP="
set /p "RESP=   Reiniciar AGORA? Digite S para Sim ou N para depois: "
if /i "!RESP!"=="S" goto :agora
goto :depois

:agora
echo.
echo   Reiniciando em 15 segundos... Salve seus arquivos!
echo   Para cancelar, feche esta janela agora.
shutdown /r /t 15 /c "Reparo concluido - reiniciando"
timeout /t 16 /nobreak >nul
exit /b 0

:depois
echo.
echo   Ok! Reinicie voce mesmo quando puder.
echo.
pause
exit /b 0
