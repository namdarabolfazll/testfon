CONTAINER_ID := $(shell docker ps -q -f name=testfon_gunicorn)

.PHONY: up down up_prod down_prod

up:
	@docker compose up --build -d
down:
	@docker compose down
up-prod:
	@docker compose -f docker-compose.prod.yml up -d
down-prod:
	@docker compose -f docker-compose.prod.yml down
migrations:
	@docker exec -it $(CONTAINER_ID) uv run python manage.py makemigrations $(filter-out $@,$(MAKECMDGOALS))
migrate:
	@docker exec -it $(CONTAINER_ID) uv run python manage.py migrate $(filter-out $@,$(MAKECMDGOALS))
manage:
	@docker exec -it $(CONTAINER_ID) uv run python manage.py $(filter-out $@,$(MAKECMDGOALS))
bash:
	@docker exec -it $(CONTAINER_ID) /bin/sh
logs:
	@docker logs $(CONTAINER_ID) -f --tail 10
%:
	@:
