# VIRTUAL ENVIROMENT LOCATION
VENV_DIR=../venvflashlingoback

ACTIVATE_VENV=. $(VENV_DIR)/bin/activate

server:
	python manage.py runserver
shell:
	python manage.py shell
setup:
	docker compose up --build -d
	docker compose exec flashlingo-back sh -c "python manage.py migrate"
	docker compose exec flashlingo-back sh -c "python manage.py load_word_dictionary"
run:
	docker compose up
stop:
	docker compose stop
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