#!/bin/bash

echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

echo "Creating static directory if it doesn't exist..."
mkdir -p static

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Running migrations..."
python3 manage.py migrate --noinput 