.PHONY: help dev-backend dev-frontend build build-backend build-frontend db-init db-migrate clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

dev-backend: ## Start backend dev server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend dev server
	cd frontend && npm run dev

build: build-backend build-frontend ## Build all Docker images

build-backend: ## Build backend Docker image
	docker compose build backend

build-frontend: ## Build frontend Docker image
	docker compose build frontend

up: ## Start all services with Docker Compose
	docker compose up -d

down: ## Stop all services
	docker compose down

db-init: ## Initialize database (create tables)
	cd backend && python -c "import asyncio; from app.database import init_db; asyncio.run(init_db())"

db-migrate: ## Create new Alembic migration
	cd backend && alembic revision --autogenerate -m "$(message)"

db-upgrade: ## Apply all pending migrations
	cd backend && alembic upgrade head

clean: ## Clean up Python cache and node_modules
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	rm -rf backend/exports frontend/dist

install: ## Install all dependencies
	cd backend && pip install -r requirements.txt
	cd frontend && npm install