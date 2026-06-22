@echo off
cd /d "%~dp0"
python atualizar_processos.py
python enviar_email.py
