# 🚀 SCRIPT DE PUBLICAÇÃO NO GITHUB - WINDOWS
# Dra. Júlia - Agente IA Advocacia
# Execute no PowerShell como Administrador

Write-Host "Dra. Julia - Agente IA Advocacia" -ForegroundColor Cyan
Write-Host "INICIANDO PUBLICACAO NO GITHUB" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

if (-not (Test-Path "README.md")) {
    Write-Host "❌ Erro: Execute este script no diretório raiz do projeto" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Verificando estrutura do projeto..." -ForegroundColor Yellow
Start-Sleep 1

$files = @("README.md", "LICENSE", "CHANGELOG.md", "CONTRIBUTING.md", ".gitignore")
foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "✅ $file encontrado" -ForegroundColor Green
    } else {
        Write-Host "❌ $file não encontrado" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🔧 Inicializando repositório Git..." -ForegroundColor Yellow
git init

Write-Host ""
Write-Host "📦 Adicionando todos os arquivos..." -ForegroundColor Yellow
git add .

Write-Host ""
Write-Host "💾 Criando commit inicial..." -ForegroundColor Yellow
git commit -m "🎉 Initial commit: Dra. Júlia - Agente IA Advocacia completo"

Write-Host ""
Write-Host "🌟 Commit criado com sucesso!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 PRÓXIMOS PASSOS MANUAIS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1️⃣ Criar repositório no GitHub:" -ForegroundColor White
Write-Host "   → Acesse: https://github.com/new" -ForegroundColor Gray
Write-Host "   → Nome: agente-dra-julia-advocacia" -ForegroundColor Gray
Write-Host "   → Visibilidade: Public" -ForegroundColor Gray
Write-Host ""
Write-Host "2️⃣ Conectar e enviar ao GitHub:" -ForegroundColor White
Write-Host "   → git remote add origin https://github.com/SEU_USUARIO/agente-dra-julia-advocacia.git" -ForegroundColor Yellow
Write-Host "   → git branch -M main" -ForegroundColor Yellow
Write-Host "   → git push -u origin main" -ForegroundColor Yellow
Write-Host ""
Write-Host "🚀 PROJETO PRONTO PARA IMPRESSIONAR! Advocacia + IA" -ForegroundColor Magenta

Read-Host "Pressione Enter para continuar..."