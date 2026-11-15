#!/usr/bin/env bash
set -o errexit

python -m pip install --upgrade pip
python -m pip install .

python src/manage.py collectstatic --no-input
python src/manage.py migrate
