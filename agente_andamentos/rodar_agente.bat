@echo off
cd /d "%~dp0"
echo [%date% %time%] Iniciando Agente de Andamentos...
python agente_andamentos.py >> logs\agente.log 2>&1
echo [%date% %time%] Concluido.
