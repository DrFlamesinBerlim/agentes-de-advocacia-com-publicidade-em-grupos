@echo off
title MABIOS v3 - Processador de E-mails WhatsApp
echo Buscando e processando exportacoes recentes do WhatsApp na INBOX do GMail...
"C:\Users\advog\Meu Drive\@ PROJETOS IAS\@ cópia de publicidade\whatsweb_bot\.venv\Scripts\python.exe" "%~dp0automacoes\process_whatsapp_exports.py"
echo.
echo Processamento concluido!
pause
