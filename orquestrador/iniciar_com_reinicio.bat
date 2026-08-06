@echo off
REM Orquestrador MABIOS — inicia e reinicia sozinho se cair
REM Coloque um atalho para ESTE arquivo na pasta de Inicialização do Windows:
REM   Win+R -> shell:startup -> cole o atalho aqui
REM Assim ele liga sozinho toda vez que a máquina inicia, e nunca fica
REM desligado (se o processo cair por qualquer motivo, reinicia em 10s).

cd /d "%~dp0"

:loop
echo [%date% %time%] Iniciando orquestrador MABIOS... >> orquestrador_startup.log
venv\Scripts\python.exe orquestrador_mabios.py >> orquestrador_startup.log 2>&1
echo [%date% %time%] Orquestrador parou. Reiniciando em 10s... >> orquestrador_startup.log
timeout /t 10 /nobreak
goto loop
