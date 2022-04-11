SHELL := /bin/bash
POETRY_VERSION=1.1.12

lint:
	mypy kafkaescli/ tests/

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

bump.%:
	poetry version $* && \
		git commit -am "bump version: $$(poetry version -s)" && \
		git push

pip-install: install-poetry
	poetry export --dev --without-hashes -f requirements.txt -o requirements.txt
	pip install -r requirements.txt

docker-build-branch:
	docker build --build-arg KAFKAESCLI_VERSION=$$(poetry version -s) -t "jonykalavera/kafkaescli:$$(poetry version -s)-$$(git branch --show-current)" .

docker-build: build
	docker build --build-arg KAFKAESCLI_VERSION=$$(poetry version -s) -t "jonykalavera/kafkaescli:$$(poetry version -s)" .

docker-push:
	docker push jonykalavera/kafkaescli:"$$(poetry version -s)-$$(git branch --show-current)"

docker-test:
	docker run -v $${pwd}:/code "jonykalavera/kafkaescli:$$(poetry version -s)-$$(git branch --show-current)" \


pipeline-test: pip-install test

pipeline-release.%: pip-install groom build
	git config --global user.email "ci-build@kafkaescli.pipeline"
	git config --global user.name "ci-build"
	$(MAKE) bump.$*
	poetry publish --username=__token__ --password=$$PYPI_API_TOKEN

pipeline-build-docs:
	cd docs/ && make html