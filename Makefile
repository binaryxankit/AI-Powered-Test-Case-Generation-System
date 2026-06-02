.PHONY: help install backend frontend dev dev-backend dev-frontend test lint typecheck build smoke clean

help:
	@echo "TestForge AI — common development tasks"
	@echo ""
	@echo "  make install         Install backend + frontend dependencies"
	@echo "  make dev             Start backend and frontend concurrently"
	@echo "  make dev-backend     Start only the FastAPI backend (port 8000)"
	@echo "  make dev-frontend    Start only the Next.js dev server (port 3000)"
	@echo "  make test            Run backend pytest suite"
	@echo "  make smoke           Run end-to-end backend smoke test"
	@echo "  make lint            Lint frontend (eslint)"
	@echo "  make typecheck       Type-check frontend (tsc --noEmit)"
	@echo "  make build           Build the production frontend bundle"
	@echo "  make migration       Generate a new Alembic migration"
	@echo "  make clean           Remove build artifacts and caches"

install:
	cd backend && python -m venv venv
	cd backend && ./venv/Scripts/python.exe -m pip install -r requirements-dev.txt || \
		./venv/bin/python -m pip install -r requirements-dev.txt
	cd frontend && npm install

dev:
	@echo "Starting backend on :8000 and frontend on :3000"
	@echo "Use Ctrl+C to stop both."
	@$(MAKE) -j2 dev-backend dev-frontend

dev-backend:
	cd backend && ./venv/Scripts/python.exe -m uvicorn backend.main:app --reload --port 8000 || \
		./venv/bin/python -m uvicorn backend.main:app --reload --port 8000

dev-frontend:
	cd frontend && npm run dev

test:
	cd backend && ./venv/Scripts/python.exe -m pytest || ./venv/bin/python -m pytest

smoke:
	cd backend && ./venv/Scripts/python.exe -m backend.scripts.smoke_test || \
		./venv/bin/python -m backend.scripts.smoke_test

lint:
	cd frontend && npm run lint

typecheck:
	cd frontend && npx tsc --noEmit

build:
	cd frontend && npm run build

migration:
	cd backend && ./venv/Scripts/python.exe -m alembic revision --autogenerate -m "$(name)" || \
		./venv/bin/python -m alembic revision --autogenerate -m "$(name)"

clean:
	rm -rf backend/venv backend/.pytest_cache backend/__pycache__ \
		backend/**/__pycache__ frontend/.next frontend/node_modules
