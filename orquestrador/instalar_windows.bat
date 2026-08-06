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
echo Proximo passo: coloque credentials.json nesta pasta e rode
echo    venv\Scripts\python.exe orquestrador_mabios.py --primeira-vez
echo para autorizar (abre o navegador, voce clica Permitir).
echo Depois disso, veja LEIA-ME.txt para deixar rodando sempre.
echo ============================================================
pause
