#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="$(pwd)"
exec .venv/bin/celery -A app.worker.celery worker -l info
