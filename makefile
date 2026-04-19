# make api          # build + start api (with db if needed)
# make api-no-deps  # build + start api only, skip db
# make up           # start all services
# make down         # stop all
# make logs         # follow api logs
# make ps           # show running containers
#
# Dev (hot-reload):
# make dev          # build + start dev api + db
# make dev-api      # build + start dev api only, skip db
# make dev-down     # stop dev services
# make dev-logs     # follow dev api logs


COMPOSE     = docker compose -f ci/docker-compose.app.yml --env-file .env
COMPOSE_DEV = docker compose -f ci/docker-compose.dev.yml --env-file .env

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

dev:
	$(COMPOSE_DEV) up -d --build

dev-api:
	$(COMPOSE_DEV) up -d --build --no-deps api

dev-down:
	$(COMPOSE_DEV) down

dev-logs:
	$(COMPOSE_DEV) logs -f api
