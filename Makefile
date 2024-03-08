CODE_FOLDERS := src db config
TEST_FOLDERS := tests

install:
	poetry install

update:
	poetry lock

db_upgrade:
	alembic upgrade head

db_seed:
	python -m seed

db_start: db_upgrade db_seed

format:
	black $(CODE_FOLDERS) $(TEST_FOLDERS)

lint:
	black --check $(CODE_FOLDERS) $(TEST_FOLDERS)
	flake8 $(CODE_FOLDERS) $(TEST_FOLDERS)
	pylint $(CODE_FOLDERS) $(TEST_FOLDERS)
	mypy $(CODE_FOLDERS) $(TEST_FOLDERS)

test:
	poetry run pytest $(TEST_FOLDER)
