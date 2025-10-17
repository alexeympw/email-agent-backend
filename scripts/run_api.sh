#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="$(pwd)"
exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
