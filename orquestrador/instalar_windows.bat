@echo off
REM Orquestrador MABIOS — instalação no Windows (rodar 1x)
REM Cria o ambiente virtual e instala as dependencias.
REM Depois disso, veja LEIA-ME.txt para autorizar e colocar na inicializacao.

cd /d "%~dp0"

echo Verificando Python...
python --version
if errorlevel 1 (
    echo.
    echo ERRO: Python nao encontrado. Instale em https://www.python.org/downloads/
    echo IMPORTANTE: marque "Add Python to PATH" durante a instalacao.
    pause
    exit /b 1
)

echo Criando ambiente virtual...
python -m venv venv

echo Instalando dependencias...
venv\Scripts\pip.exe install -r requirements.txt

echo.
echo ============================================================
echo Instalacao concluida.
echo Proximo passo: veja LEIA-ME.txt para:
echo 1. Instalar gcloud CLI (se ainda nao tiver)
echo 2. Autorizar com: gcloud auth application-default login
echo 3. Testar com: venv\Scripts\python.exe orquestrador_mabios.py --primeira-vez
echo 4. Deixar rodando sempre (startup folder)
echo ============================================================
pause
