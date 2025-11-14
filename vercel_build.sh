#!/bin/bash

# Criar diretório static se não existir
mkdir -p static

# Coletar arquivos estáticos
python3 manage.py collectstatic --noinput 