.PHONY: help up down restart logs pull-models migrations migrate shell status clean

COMPOSE = docker compose

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

up: ## Start all services
	$(COMPOSE) up -d

down: ## Stop all services
	$(COMPOSE) down

restart: ## Restart all services
	$(COMPOSE) restart

logs: ## Tail logs for all services
	$(COMPOSE) logs -f

logs-app: ## Tail app logs
	$(COMPOSE) logs -f app

status: ## Show service status
	$(COMPOSE) ps

pull-models: ## Pull Ollama models (nomic-embed-text, llama3.2:1b)
	$(COMPOSE) exec ollama ollama pull nomic-embed-text
	$(COMPOSE) exec ollama ollama pull llama3.2:1b

migrations: ## Generate a new migration
	$(COMPOSE) exec app alembic revision --autogenerate -m "$(msg)"

migrate: ## Run database migrations
	$(COMPOSE) exec app alembic upgrade head

shell: ## Open a shell in the app container
	$(COMPOSE) exec app bash

psql: ## Connect to PostgreSQL
	$(COMPOSE) exec postgres psql -U $${POSTGRES_USER:-retrievix} -d $${POSTGRES_DB:-retrievix}

clean: ## Remove all containers, volumes, and images
	$(COMPOSE) down -v --rmi all
