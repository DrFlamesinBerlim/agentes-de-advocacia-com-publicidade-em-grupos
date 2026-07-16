@echo off
setlocal enabledelayedexpansion
title Instalador de Atalhos - Windows Optimizer Suite
cls
color 0B

echo ================================================================================
echo.
echo            INSTALADOR DE ATALHOS - WINDOWS OPTIMIZER SUITE
echo.
echo ================================================================================
echo.
echo Isso vai criar 4 icones na sua Area de Trabalho, cada um pronto para
echo executar com um clique duplo:
echo.
echo   1. Reparar Touchpad
echo   2. Limpar Sistema (Previa - Seguro, nada e deletado)
echo   3. Limpar Sistema (Aplicar Mudancas)
echo   4. Dashboard Otimizador
echo.
echo ================================================================================
echo.
pause

set "SCRIPT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
set "VBS=%TEMP%\criar_atalho_temp.vbs"

echo.
echo Criando atalhos...
echo.

REM ---- Atalho 1: Reparar Touchpad ----
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%DESKTOP%\Reparar Touchpad.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%SCRIPT_DIR%launcher_reparar_touchpad.bat"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%"
echo oLink.IconLocation = "shell32.dll,71"
echo oLink.Description = "Repara o touchpad/mousepad do notebook"
echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%"
echo   [OK] Reparar Touchpad

REM ---- Atalho 2: Limpar Previa ----
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%DESKTOP%\Limpar Sistema - Previa.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%SCRIPT_DIR%launcher_limpar_preview.bat"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%"
echo oLink.IconLocation = "shell32.dll,238"
echo oLink.Description = "Mostra previa do que sera limpo - nada e deletado"
echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%"
echo   [OK] Limpar Sistema - Previa

REM ---- Atalho 3: Limpar Aplicar ----
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%DESKTOP%\Limpar Sistema - Aplicar.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%SCRIPT_DIR%launcher_limpar_aplicar.bat"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%"
echo oLink.IconLocation = "shell32.dll,32"
echo oLink.Description = "Executa a limpeza de verdade - cria restore point antes"
echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%"
echo   [OK] Limpar Sistema - Aplicar

REM ---- Atalho 4: Dashboard ----
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%DESKTOP%\Dashboard Otimizador.lnk"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%SCRIPT_DIR%launcher_abrir_dashboard.bat"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%"
echo oLink.IconLocation = "shell32.dll,13"
echo oLink.Description = "Abre o dashboard de monitoramento"
echo oLink.Save
) > "%VBS%"
cscript //nologo "%VBS%"
echo   [OK] Dashboard Otimizador

del "%VBS%" >nul 2>&1

echo.
echo ================================================================================
echo.
echo   TUDO PRONTO! 4 icones foram criados na sua Area de Trabalho.
echo.
echo   Va ate a Area de Trabalho e clique duas vezes no icone que quiser usar.
echo.
echo ================================================================================
echo.
pause
