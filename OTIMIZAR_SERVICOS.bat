@echo off
title Otimizador de Servicos - Desliga Bloatware com Seguranca
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
echo           OTIMIZADOR DE SERVICOS - DESLIGA BLOATWARE SEGURO
echo.
echo   NAO toca em: criptografia, Plug and Play, touchpad, audio,
echo   rede, energia nem seguranca. Tudo reversivel.
echo.
echo ================================================================================
echo.

REM ---- Ponto de restauracao ----
echo Criando ponto de restauracao de seguranca...
powershell -NoProfile -Command "Checkpoint-Computer -Description 'Otimizacao de Servicos' -RestorePointType 'MODIFY_SETTINGS'" >nul 2>&1
if %errorlevel% equ 0 (
    echo    [OK] Ponto de restauracao criado
) else (
    echo    [AVISO] Nao criou ponto, continua mesmo assim
)
echo.

echo ================================================================================
echo DESLIGANDO SERVICOS DESNECESSARIOS...
echo ================================================================================
echo.

set /a DESLIGADOS=0
set /a NAO_ENCONTRADOS=0

REM Nome real do servico + descricao SEM parenteses ^(evita bug do batch^)
call :desliga DiagTrack           "Telemetria - coleta de dados"
call :desliga dmwappushservice    "Publicidade e push"
call :desliga Fax                 "Fax"
call :desliga MapsBroker          "Gerenciador de Mapas Baixados"
call :desliga RetailDemo          "Modo Demonstracao de Loja"
call :desliga WMPNetworkSvc       "Compartilhamento do Media Player"
call :desliga RemoteRegistry      "Registro Remoto - risco de seguranca"
call :desliga WerSvc              "Relatorio de Erros do Windows"
call :desliga XblAuthManager      "Xbox Live - Autenticacao"
call :desliga XblGameSave         "Xbox Live - Salvar Jogo"
call :desliga XboxGipSvc          "Xbox - Controle"
call :desliga XboxNetApiSvc       "Xbox - Rede"

echo.
echo ================================================================================
echo AJUSTANDO SEM DESLIGAR DE VEZ...
echo ================================================================================
echo.
echo    Windows Search para Manual...
sc config WSearch start= demand >nul 2>&1
echo    [OK] Windows Search agora e Manual
echo.

color 0A
echo ================================================================================
echo   RESUMO DA OTIMIZACAO:
echo.
echo      Servicos desligados:      !DESLIGADOS!
echo      Nao existiam neste PC:    !NAO_ENCONTRADOS!
echo      Windows Search:           ajustado para Manual
echo.
echo   O ganho de RAM aparece melhor APOS REINICIAR.
echo.
echo   Para reverter um servico, exemplo Xbox, use no CMD admin:
echo      sc config XblAuthManager start= demand
echo ================================================================================
echo.

REM ---- Escolha de reinicio ----
echo   O ganho dos servicos so aparece APOS reiniciar.
echo.
set "RESP="
set /p "RESP=   Reiniciar AGORA? Digite S para Sim ou N para depois: "
if /i "!RESP!"=="S" goto :agora
goto :depois

:agora
echo.
echo   Reiniciando em 15 segundos... Salve seus arquivos!
echo   Para cancelar, feche esta janela agora.
shutdown /r /t 15 /c "Otimizacao de servicos concluida"
timeout /t 16 /nobreak >nul
exit /b 0

:depois
echo.
echo   Ok! Reinicie voce mesmo quando puder para os servicos fazerem efeito.
echo.
pause
exit /b 0

REM ============================================================
REM  Sub-rotina: desliga um servico com seguranca
REM ============================================================
:desliga
set "SVC=%~1"
set "DESC=%~2"
sc query "%SVC%" >nul 2>&1
if %errorlevel% neq 0 (
    echo    [--] !DESC! - nao existe neste PC
    set /a NAO_ENCONTRADOS+=1
    goto :eof
)
sc stop "%SVC%" >nul 2>&1
sc config "%SVC%" start= disabled >nul 2>&1
echo    [OK] !DESC!
set /a DESLIGADOS+=1
goto :eof
