#!/bin/bash
# Script de build para Vercel

echo "🚀 Iniciando build do projeto..."

# Instalar dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Executar migrações
echo "🗄️ Executando migrações do banco de dados..."
python manage.py migrate --noinput

echo "✅ Build concluído com sucesso!"