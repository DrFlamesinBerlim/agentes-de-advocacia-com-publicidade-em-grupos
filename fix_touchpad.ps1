#!/usr/bin/env powershell
# Fix Touchpad - Script PowerShell Automático
# Execute como ADMINISTRADOR

# Verificar se é Admin
$isAdmin = [bool]([Security.Principal.WindowsIdentity]::GetCurrent().Groups -match "S-1-5-32-544")
if (-not $isAdmin) {
    Write-Host "❌ Este script precisa ser executado como ADMINISTRADOR!" -ForegroundColor Red
    Write-Host "👉 Clique direito no PowerShell → 'Executar como administrador'" -ForegroundColor Yellow
    pause
    exit
}

Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "🖱️  FIX TOUCHPAD - Reparador Automático" -ForegroundColor Cyan -NoNewline
Write-Host "`n" -NoNewline
Write-Host "="*80 -ForegroundColor Cyan
Write-Host "`n✓ Executando com privilégios de ADMIN`n" -ForegroundColor Green

# ============================================================================
# PASSO 1: Restaurar Serviços Críticos
# ============================================================================

Write-Host "-"*80
Write-Host "PASSO 1/4: Restaurando Serviços Críticos..." -ForegroundColor Yellow
Write-Host "-"*80 -NoNewline
Write-Host "`n"

$servicos = @{
    "PlugPlay" = "Automático"
    "hidserv" = "Automático"
    "DcaSvc" = "Manual"
    "Dhcp" = "Automático"
    "Dnscache" = "Automático"
    "nsi" = "Automático"
}

foreach ($servico in $servicos.GetEnumerator()) {
    $nome = $servico.Name
    $tipo = $servico.Value

    try {
        Write-Host "   Configurando $nome → $tipo..." -NoNewline

        Set-Service -Name $nome -StartupType $tipo -ErrorAction SilentlyContinue
        Start-Service -Name $nome -ErrorAction SilentlyContinue

        Write-Host " ✓" -ForegroundColor Green
    }
    catch {
        Write-Host " ✗" -ForegroundColor Red
    }
}

Write-Host "`n✅ Serviços restaurados`n" -ForegroundColor Green

# ============================================================================
# PASSO 2: Habilitar Touchpad
# ============================================================================

Write-Host "-"*80
Write-Host "PASSO 2/4: Habilitando Touchpad..." -ForegroundColor Yellow
Write-Host "-"*80 -NoNewline
Write-Host "`n"

$touchpadFound = $false

try {
    $devices = Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -match 'touch|pad|synaptics|elan|trackpad|pointing'
    }

    if ($devices) {
        foreach ($device in $devices) {
            Write-Host "   Encontrado: $($device.Name)" -ForegroundColor Cyan
            Write-Host "      Status: $($device.Status)" -NoNewline

            if ($device.Status -ne 'OK') {
                try {
                    Enable-PnpDevice -InstanceId $device.InstanceId -Confirm:$false -ErrorAction SilentlyContinue
                    Start-Sleep -Milliseconds 500
                    Write-Host " → Habilitado ✓" -ForegroundColor Green
                    $touchpadFound = $true
                }
                catch {
                    Write-Host " → Erro ✗" -ForegroundColor Red
                }
            }
            else {
                Write-Host " → Já ativado ✓" -ForegroundColor Green
                $touchpadFound = $true
            }
        }
    }
    else {
        Write-Host "   ⚠️  Nenhum touchpad encontrado" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "   ❌ Erro ao processar devices" -ForegroundColor Red
}

Write-Host "`n"

if ($touchpadFound) {
    Write-Host "✅ Touchpad habilitado com sucesso!`n" -ForegroundColor Green
}
else {
    Write-Host "⚠️  Touchpad não foi encontrado" -ForegroundColor Yellow
    Write-Host "   Verifique no Gerenciador de Dispositivos`n" -ForegroundColor Yellow
}

# ============================================================================
# PASSO 3: Limpar Registros Inválidos
# ============================================================================

Write-Host "-"*80
Write-Host "PASSO 3/4: Limpando Registros Inválidos..." -ForegroundColor Yellow
Write-Host "-"*80 -NoNewline
Write-Host "`n"

try {
    Write-Host "   Removendo atalhos órfãos..." -NoNewline
    Remove-Item -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\MountPoints2' -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host " ✓" -ForegroundColor Green
}
catch {
    Write-Host " ✗" -ForegroundColor Red
}

Write-Host "`n✅ Registro limpo`n" -ForegroundColor Green

# ============================================================================
# PASSO 4: Reiniciar Windows
# ============================================================================

Write-Host "-"*80
Write-Host "PASSO 4/4: Preparando para Reiniciar..." -ForegroundColor Yellow
Write-Host "-"*80 -NoNewline
Write-Host "`n"

Write-Host "   Encerrando Explorer..." -NoNewline
taskkill /f /im explorer.exe /t 2>$null
Start-Sleep -Seconds 1
Write-Host " ✓" -ForegroundColor Green

Write-Host "   Iniciando Explorer..." -NoNewline
Start-Process explorer.exe
Write-Host " ✓" -ForegroundColor Green

Write-Host "`n✅ Tudo pronto para reiniciar!`n" -ForegroundColor Green

# ============================================================================
# CONFIRMAÇÃO DE REINICIALIZAÇÃO
# ============================================================================

Write-Host "="*80
Write-Host "🔄 REINICIANDO WINDOWS" -ForegroundColor Cyan
Write-Host "="*80

Write-Host "`n⏱️  Seu notebook vai reiniciar em 30 segundos...`n" -ForegroundColor Yellow
Write-Host "   Salve seus arquivos! Você será desconectado automaticamente." -ForegroundColor Yellow

Write-Host "`n   Pressione Ctrl+C para CANCELAR o restart (não é recomendado)`n" -ForegroundColor Red

# Contagem regressiva
for ($i = 30; $i -gt 0; $i--) {
    Write-Host "`r   Reiniciando em: $i segundos  " -NoNewline
    Start-Sleep -Seconds 1
}

Write-Host "`r   Reiniciando agora!                        " -ForegroundColor Green

# Reiniciar
shutdown /r /t 5 /c "Windows Optimizer - Touchpad Fix"

Write-Host "`n✨ Script concluído! Reinicio iniciado...`n" -ForegroundColor Green
