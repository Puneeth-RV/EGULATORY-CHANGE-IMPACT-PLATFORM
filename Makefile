.PHONY: install test test-backend test-frontend build run-api run-web

install:
	python3.11 -m venv .venv
	.venv/bin/pip install -r requirements.txt
	cd frontend && npm install

test: test-backend test-frontend

test-backend:
	.venv/bin/python -m pytest -q

test-frontend:
	cd frontend && npm test

build:
	cd frontend && npm run build

run-api:
	.venv/bin/uvicorn backend.main:app --reload --port 8000

run-web:
	cd frontend && npm run dev
