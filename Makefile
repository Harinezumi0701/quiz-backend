COMPOSE = docker compose -f ci/docker-compose.app.yml --env-file .env

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

build:
	$(COMPOSE) up -d --build

api:
	$(COMPOSE) up -d --build api

api-no-deps:
	$(COMPOSE) up -d --build --no-deps api

logs:
	$(COMPOSE) logs -f api

ps:
	$(COMPOSE) ps
