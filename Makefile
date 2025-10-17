PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
UVICORN ?= .venv/bin/uvicorn
CELERY ?= .venv/bin/celery
ALEMBIC ?= .venv/bin/alembic

export PYTHONPATH := $(shell pwd)

.PHONY: venv install dev run api worker migrate upgrade downgrade

venv:
	python3.11 -m venv .venv

install: venv
	$(PIP) install -r requirements.txt

dev: install
	@echo "Dev env ready."

api:
	$(UVICORN) app.main:app --reload

worker:
	$(CELERY) -A app.worker.celery worker -l info

migrate:
	$(ALEMBIC) revision --autogenerate -m "auto"

upgrade:
	$(ALEMBIC) upgrade head

downgrade:
	$(ALEMBIC) downgrade -1
