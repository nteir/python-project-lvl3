install:
	poetry install

build:
	poetry build

package-install:
	python3 -m pip install --user --force dist/*.whl

lint:
	poetry run flake8 gendiff

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=gendiff tests/ --cov-report xml

.PHONY: install build package-install lint test test-cov