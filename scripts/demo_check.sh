#!/usr/bin/env sh
set -eu

echo "Checking backend tests…"
.venv/bin/python -m pytest -q

echo "Checking frontend tests and production build…"
(cd frontend && npm test && npm run build)

echo "All local verification checks passed."
