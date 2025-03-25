# VIRTUAL ENVIROMENT LOCATION
VENV_DIR=../venvflashlingoback

ACTIVATE_VENV=. $(VENV_DIR)/bin/activate

server:
	python manage.py runserver
shell:
	python manage.py shell
run:
	@echo "Activating virtual environment and starting server"
	$(ACTIVATE_VENV) && python manage.py runserver
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