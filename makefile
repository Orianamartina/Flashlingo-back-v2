# VIRTUAL ENVIROMENT LOCATION
VENV_DIR=../venvflashlingoback

ACTIVATE_VENV=. $(VENV_DIR)/bin/activate

server:
	python manage.py runserver
shell:
	python manage.py shell
setup:
	docker compose up --build
run:
	docker compose up
down:
	docker compose down
migrate:
	python manage.py migrate
migrations:
	python manage.py makemigrations
test:
	python manage.py test
lint:
	black .
socket:
	daphne -p 8001 flashlingo.asgi:application