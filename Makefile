.PHONY: install test run up down
install:
	pip install -e ".[dev]"
test:
	pytest -q
run:
	uvicorn agentshield.main:app --reload
up:
	docker compose up --build -d
down:
	docker compose down -v
