#!/bin/bash
set -e  # Para parar o build se houver erro

# Remove diretório antigo de estáticos (se existir)
rm -rf staticfiles_build

# Cria diretório novo
mkdir -p staticfiles_build

# Coleta arquivos estáticos do Django
python3 manage.py collectstatic --noinput

echo "Static files collected to staticfiles_build ✅"
