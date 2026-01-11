#!/bin/bash
echo "Building project..."
python3 -m pip install -r requirements.txt

echo "Collect Static..."
python3 manage.py collectstatic --noinput --clear

echo "Running Migrations..."
python3 manage.py migrate
