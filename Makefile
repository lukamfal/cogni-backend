.PHONY: run dev migrate upgrade install

install:
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

migrate:
	alembic revision --autogenerate -m "$(msg)"

upgrade:
	alembic upgrade head

docker-up:
	docker compose up --build

docker-down:
	docker compose down

shell:
	python -c "from app.core.database import engine; from app.models import *; Base.metadata.create_all(engine); print('Tabelas criadas!')"
