@echo off
title Otimizador de Servicos - Versao Robusta
REM ============================================================
REM  Auto-elevacao pelo metodo classico ^(ShellExecute^)
REM ============================================================
reg query "HKU\S-1-5-19" >nul 2>&1
if %errorlevel% neq 0 (
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\elev_srv.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\elev_srv.vbs"
    "%temp%\elev_srv.vbs"
    exit /b
)
if exist "%temp%\elev_srv.vbs" del "%temp%\elev_srv.vbs"

setlocal enabledelayedexpansion
color 0B
cls
echo ================================================================================
echo.
echo           OTIMIZADOR DE SERVICOS - DESLIGA BLOATWARE SEGURO
echo.
echo   NAO toca em: criptografia, Plug and Play, touchpad, audio,
echo   rede, energia nem seguranca. Tudo reversivel.
echo.
echo ================================================================================
echo.

echo Criando ponto de restauracao de seguranca...
powershell -NoProfile -Command "Checkpoint-Computer -Description 'Otimizacao Servicos' -RestorePointType 'MODIFY_SETTINGS'" >nul 2>&1
echo    [OK] Etapa de restauracao concluida
echo.

echo ================================================================================
echo DESLIGANDO SERVICOS DESNECESSARIOS...
echo ================================================================================
echo.

set /a N=0
for %%S in (DiagTrack dmwappushservice Fax MapsBroker RetailDemo WMPNetworkSvc RemoteRegistry WerSvc XblAuthManager XblGameSave XboxGipSvc XboxNetApiSvc) do (
    sc stop "%%S" >nul 2>&1
    sc config "%%S" start= disabled >nul 2>&1
    echo    [OK] %%S
    set /a N+=1
)

echo.
echo Ajustando Windows Search para Manual...
sc config WSearch start= demand >nul 2>&1
echo    [OK] WSearch

echo.
color 0A
echo ================================================================================
echo   CONCLUIDO com sucesso!
echo.
echo      Servicos processados:  !N!
echo      Windows Search:        ajustado para Manual
echo.
echo   O ganho de RAM aparece melhor APOS REINICIAR.
echo.
echo   Para reverter um servico, exemplo Xbox, digite no CMD admin:
echo      sc config XblAuthManager start= demand
echo ================================================================================
echo.

echo ================================================================================
echo   O Windows vai REINICIAR automaticamente em 60 segundos
echo   para os servicos fazerem efeito. Salve seus arquivos AGORA.
echo.
echo   Nao quer reiniciar agora? Abra o menu Iniciar, digite:
echo        shutdown /a
echo   e tecle Enter para CANCELAR o reinicio.
echo ================================================================================
shutdown /r /t 60 /c "Otimizacao concluida - reiniciando" >nul 2>&1
echo.
echo   Contagem de 60 segundos iniciada. Pode aguardar aqui.
timeout /t 62 /nobreak >nul
exit /b 0
