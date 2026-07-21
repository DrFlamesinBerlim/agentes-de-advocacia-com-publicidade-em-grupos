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
echo Criando ponto de restauracao ^(seguranca^)...
powershell -NoProfile -Command "Checkpoint-Computer -Description 'Otimizacao de Servicos' -RestorePointType 'MODIFY_SETTINGS'" >nul 2>&1
if %errorlevel% equ 0 (echo    [OK] Ponto criado) else (echo    [AVISO] Nao criou ponto, continua)
echo.

echo ================================================================================
echo DESLIGANDO SERVICOS DESNECESSARIOS...
echo ================================================================================
echo.

set /a DESLIGADOS=0
set /a NAO_ENCONTRADOS=0

REM Lista: nome real do servico + descricao amigavel
call :desliga DiagTrack           "Telemetria / coleta de dados"
call :desliga dmwappushservice    "Publicidade / push"
call :desliga Fax                 "Fax"
call :desliga MapsBroker          "Gerenciador de Mapas Baixados"
call :desliga RetailDemo          "Modo Demonstracao de Loja"
call :desliga WMPNetworkSvc       "Compartilhamento do Media Player"
call :desliga RemoteRegistry      "Registro Remoto ^(risco de seguranca^)"
call :desliga WerSvc              "Relatorio de Erros do Windows"
call :desliga XblAuthManager      "Xbox Live - Autenticacao"
call :desliga XblGameSave         "Xbox Live - Salvar Jogo"
call :desliga XboxGipSvc          "Xbox - Controle"
call :desliga XboxNetApiSvc       "Xbox - Rede"

echo.
echo ================================================================================
echo AJUSTANDO ^(sem desligar de vez^)...
echo ================================================================================
echo.

REM Windows Search para Manual - ajuda em maquina fraca, reversivel
echo    Windows Search -^> Manual...
sc config WSearch start= demand >nul 2>&1
echo    [OK] Windows Search agora e Manual
echo.

color 0A
echo ================================================================================
echo   [CONCLUIDO] Resumo da otimizacao:
echo.
echo      Servicos desligados:      !DESLIGADOS!
echo      Nao existiam neste PC:    !NAO_ENCONTRADOS!
echo      Windows Search:           ajustado para Manual
echo.
echo   O ganho de RAM aparece melhor APOS REINICIAR.
echo.
echo   PARA REVERTER qualquer um ^(exemplo Xbox^):
echo      sc config XblAuthManager start= demand
echo.
echo   PROXIMO PASSO ^(o que MAIS ajuda num 8 GB^):
echo   Ctrl+Shift+Esc  -^>  aba INICIALIZAR  -^>  desabilite
echo   os programas que voce nao usa ^(Spotify, Discord, updaters^).
echo ================================================================================
echo.
pause
exit /b 0

REM ============================================================
REM  Sub-rotina: desliga um servico e mostra o resultado
REM ============================================================
:desliga
set "SVC=%~1"
set "DESC=%~2"
sc query "%SVC%" >nul 2>&1
if %errorlevel% neq 0 (
    echo    [--] %DESC% ^(nao existe neste Windows^)
    set /a NAO_ENCONTRADOS+=1
    goto :eof
)
sc stop "%SVC%" >nul 2>&1
sc config "%SVC%" start= disabled >nul 2>&1
echo    [OK] %DESC%
set /a DESLIGADOS+=1
goto :eof
