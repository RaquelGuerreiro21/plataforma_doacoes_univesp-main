#!/bin/bash

# Limpa a pasta staticfiles para garantir arquivos atualizados
rm -rf staticfiles
mkdir -p staticfiles

# Coletar arquivos estáticos
python3 manage.py collectstatic --noinput

# Opcional: mostrar conteúdo para debug
ls -la staticfiles
