#!/bin/sh
sleep 15

alembic revision --autogenerate -m "db migration in container"
alembic upgrade head

python main.py
