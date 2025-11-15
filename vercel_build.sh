#!/bin/bash
rm -rf staticfiles_build
mkdir staticfiles_build
python3 manage.py collectstatic --noinput
chmod +x vercel_build.sh
