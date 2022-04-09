POETRY_VERSION=1.1.12
test:
	mkdir test-results
	python -m pytest --cov --junitxml=test-results/junit.xml tests/
	python -m coverage report
	python -m coverage html  # open htmlcov/index.html in a browser

groom:
	isort kafkescli/ tests/
	black kafkescli/ tests/


install-poetry:
	POETRY_VERSION=$(POETRY_VERSION) curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

make build:
	poetry build

install:
	poetry install

pip-install:
	poetry export --dev --without-hashes -f requirements.txt -o requirements.txt
	pip install -r requirements.txt

docker-build: build
	@docker build -t kafkescli: .

docker-run:
	docker run -it --rm --name kafkescli kafkescli

pipeline-test: install-poetry pip-install test

pipeline-release.%: install-poetry pip-install groom build
	poetry version $*
	git commit -am "bump version: $$(poetry version)"
