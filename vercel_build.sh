#!/bin/bash

# Remove diretório antigo de estáticos (se existir)
rm -rf staticfiles_build

# Cria diretório novo
mkdir staticfiles_build

# Coleta arquivos estáticos do Django
python3 manage.py collectstatic --noinput
