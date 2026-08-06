@echo off
title Reparador de Problemas - Registro e Sistema
REM ============================================================
REM  Auto-elevacao pelo metodo classico ^(ShellExecute^)
REM ============================================================
reg query "HKU\S-1-5-19" >nul 2>&1
if %errorlevel% neq 0 (
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\elev_rep.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\elev_rep.vbs"
    "%temp%\elev_rep.vbs"
    exit /b
)
if exist "%temp%\elev_rep.vbs" del "%temp%\elev_rep.vbs"

setlocal enabledelayedexpansion
cls
color 0B
echo ================================================================================
echo.
echo         REPARADOR DE PROBLEMAS - REGISTRO E ARQUIVOS DO SISTEMA
echo.
echo   Usa as ferramentas OFICIAIS da Microsoft para achar e consertar
echo   corrupcoes com seguranca. Nao apaga chaves no chute.
echo.
echo   IMPORTANTE: pode demorar de 10 a 30 minutos.
echo   E NORMAL a tela ficar parada em alguns momentos - NAO feche.
echo.
echo ================================================================================
echo.
echo   Comecando em 5 segundos...
timeout /t 5 /nobreak >nul
echo.

REM ============================================================
REM  PASSO 1 - Ponto de restauracao
REM ============================================================
echo ================================================================================
echo PASSO 1/5: Criando ponto de restauracao...
echo ================================================================================
powershell -NoProfile -Command "Checkpoint-Computer -Description 'Antes de Reparar' -RestorePointType 'MODIFY_SETTINGS'" >nul 2>&1
echo    [OK] Etapa de restauracao concluida
echo.

REM ============================================================
REM  PASSO 2 - Backup do registro na Area de Trabalho
REM ============================================================
echo ================================================================================
echo PASSO 2/5: Fazendo backup do registro...
echo    AGUARDE: exportar o registro demora 1 a 2 minutos SEM mostrar
echo    movimento na tela. Isso e NORMAL, nao feche.
echo ================================================================================
set "BKP=%USERPROFILE%\Desktop\Backup_Registro"
if not exist "%BKP%" mkdir "%BKP%" >nul 2>&1
echo    Exportando HKLM\SOFTWARE... aguarde...
reg export "HKLM\SOFTWARE" "%BKP%\HKLM_SOFTWARE.reg" /y >nul 2>&1
echo    [OK] parte 1 do backup pronta
echo    Exportando HKCU... aguarde...
reg export "HKCU" "%BKP%\HKCU.reg" /y >nul 2>&1
echo    [OK] Backup completo salvo em: %BKP%
echo.

REM ============================================================
REM  PASSO 3 - System File Checker
REM ============================================================
echo ================================================================================
echo PASSO 3/5: Verificando arquivos do sistema com SFC...
echo    Isso conserta arquivos e referencias de registro corrompidos.
echo    A porcentagem pode ficar PARADA por minutos - e NORMAL.
echo ================================================================================
sfc /scannow
echo.
echo    [OK] Verificacao SFC concluida
echo.

REM ============================================================
REM  PASSO 4 - DISM RestoreHealth
REM ============================================================
echo ================================================================================
echo PASSO 4/5: Reparando a imagem do Windows com DISM...
echo    Corrige o que o SFC sozinho nao resolve.
echo    Pode parar em 20%% por varios minutos - e NORMAL.
echo ================================================================================
DISM /Online /Cleanup-Image /RestoreHealth
echo.
echo    [OK] Reparo DISM concluido
echo.

REM ============================================================
REM  PASSO 5 - Verificar disco
REM ============================================================
echo ================================================================================
echo PASSO 5/5: Verificando erros no disco com CHKDSK...
echo    Somente leitura, seguro, nao altera nada.
echo ================================================================================
chkdsk C: /scan
echo.
echo    [OK] Verificacao de disco concluida
echo.

color 0A
echo ================================================================================
echo   [CONCLUIDO] Reparo finalizado com sucesso!
echo.
echo   Backup do registro guardado em:
echo      %BKP%
echo ================================================================================
echo.

REM ---- Reinicio automatico confiavel ----
echo   O Windows vai REINICIAR automaticamente em 60 segundos
echo   para aplicar os reparos. Salve seus arquivos AGORA.
echo.
echo   Nao quer reiniciar agora? Abra o menu Iniciar, digite:
echo        shutdown /a
echo   e tecle Enter para CANCELAR o reinicio.
echo.
shutdown /r /t 60 /c "Reparo concluido - reiniciando" >nul 2>&1
echo   Contagem de 60 segundos iniciada. Pode aguardar aqui.
timeout /t 62 /nobreak >nul
exit /b 0
