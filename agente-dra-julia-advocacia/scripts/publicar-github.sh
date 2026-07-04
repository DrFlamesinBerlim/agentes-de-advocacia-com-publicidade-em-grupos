#!/bin/bash

# 🚀 Script de Publicação no GitHub - Dra. Júlia Advocacia

echo "🏛️ INICIANDO PUBLICAÇÃO DA DRA. JÚLIA NO GITHUB ⚖️"
echo "=================================================="

if [ ! -f "README.md" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    exit 1
fi

echo "📁 Verificando estrutura do projeto..."
sleep 1

files=("README.md" "LICENSE" "CHANGELOG.md" "CONTRIBUTING.md" ".gitignore")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file encontrado"
    else
        echo "❌ $file não encontrado"
        exit 1
    fi
done

echo ""
echo "🔧 Inicializando repositório Git..."
git init

echo ""
echo "📦 Adicionando todos os arquivos..."
git add .

echo ""
echo "💾 Criando commit inicial..."
git commit -m "🎉 Initial commit: Dra. Júlia - Agente IA Advocacia completo"

echo ""
echo "🌟 Commit criado com sucesso!"
echo ""
echo "📋 PRÓXIMOS PASSOS MANUAIS:"
echo "=========================="
echo ""
echo "1️⃣ Criar repositório no GitHub:"
echo "   → Acesse: https://github.com/new"
echo "   → Nome: agente-dra-julia-advocacia"
echo "   → Visibilidade: Public"
echo ""
echo "2️⃣ Conectar e enviar ao GitHub:"
echo "   → git remote add origin https://github.com/SEU_USUARIO/agente-dra-julia-advocacia.git"
echo "   → git branch -M main"
echo "   → git push -u origin main"
echo ""
echo "🚀 PROJETO PRONTO PARA IMPRESSIONAR! ⚖️👩‍💼"
echo ""