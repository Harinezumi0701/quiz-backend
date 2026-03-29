# make api          # build + start api (with db if needed)
# make api-no-deps  # build + start api only, skip db
# make up           # start all services
# make down         # stop all
# make logs         # follow api logs
# make ps           # show running containers


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
