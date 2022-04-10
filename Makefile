SHELL := /bin/bash
POETRY_VERSION=1.1.12

test:
	mkdir -p test-results
	pytest --cov=kafkaescli --junitxml=test-results/junit.xml tests/
	coverage report
	coverage html  # open htmlcov/index.html in a browser

groom:
	isort kafkaescli/ tests/
	black kafkaescli/ tests/


install-poetry:
	pip install pip --upgrade
	pip install poetry==$(POETRY_VERSION)

make build:
	poetry build

install:
	poetry install

pip-install: install-poetry
	poetry export --dev --without-hashes -f requirements.txt -o requirements.txt
	pip install -r requirements.txt

docker-build: build
	docker build --build-arg KAFKAESCLI_VERSION=$$(poetry version -s) -t "jonykalavera/kafkaescli:$$(poetry version -s)-$$(git branch --show-current)" .

docker-push:
	docker push jonykalavera/kafkaescli:"$$(poetry version -s)-$$(git branch --show-current)"

docker-run-tests:
	docker run \
		-v $(realpath .):/code \
		--workdir /code \
		"jonykalavera/kafkaescli:$$(poetry version -s)-$$(git branch --show-current)" \
		make pip-install test

pipeline-test: pip-install test

pipeline-release.%: pip-install groom build
	VERSION=$* poetry version $$VERSION && git commit -am "bump $$VERSION version: $$(poetry version -s)"

pipeline-build-docs:
	cd docs/ && make html