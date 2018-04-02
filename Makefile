ts ?= 5

autogenerate: build_db
	docker-compose run schema alembic revision --autogenerate


build_db:
	docker-compose up -d postgres
	sleep $(ts)


apply:
	docker-compose run schema alembic upgrade head


run_api:
	docker-compose up api


run: build_db apply run_api


build:
	docker-compose build


test_unit:
	docker-compose run --rm unittest pytest -s -v tests/unit


test_functional:
	docker-compose run --rm unittest pytest -s -v tests/functional
