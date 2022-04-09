POETRY_VERSION=1.1.12
test:
	pylint kafkescli/ tests/
	pytest tests/
	mypy kafkescli/ tests/

groom:
	isort kafkescli/ tests/
	black kafkescli/ tests/


install-poetry:
	POETRY_VERSION=$(POETRY_VERSION) curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

make build:
	poetry build

install:
	poetry install

docker-build: build
	@docker build -t kafkescli: .

docker-run:
	docker run -it --rm --name kafkescli kafkescli

pipeline-test: install-poetry install test

pipeline-release.%: install-poetry install groom build
	poetry version $*
	git commit -am "bump version: $$(poetry version)"
