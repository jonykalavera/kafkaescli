SHELL := /bin/bash
POETRY_VERSION=1.1.12

lint:
	mypy kafkaescli/ tests/

test:
	mkdir -p test-results
	pytest --cov=kafkaescli --junitxml=test-results/junit.xml tests/
	coverage report

groom:
	isort kafkaescli/ tests/
	black kafkaescli/ tests/


install-poetry:
	pip install pip --upgrade
	pip install poetry==$(POETRY_VERSION)

build:
	poetry build

install:
	poetry install

bump.%:
	poetry version $* && \
		git commit -am "bump version: $$(poetry version -s)" && \
		git push

diagrams.%:
	rm -fr docs/diagrams/*.$*
	pyreverse -d ./docs/diagrams --colorized -o "$*" -s 1 -p kafkaescli.core.shared kafkaescli.core.shared
	pyreverse -d ./docs/diagrams --colorized -o "$*" -s 1 -p kafkaescli.core.config kafkaescli.core.config
	pyreverse -d ./docs/diagrams --colorized -o "$*" -s 1 -p kafkaescli.core.middleware kafkaescli.core.middleware
	pyreverse -d ./docs/diagrams --colorized -o "$*" -s 1 -p kafkaescli.core.consumer kafkaescli.core.consumer
	pyreverse -d ./docs/diagrams --colorized -o "$*" -s 1 -p kafkaescli.core.producer kafkaescli.core.producer
	pyreverse -d ./docs/diagrams --colorized -o "$*" -s 1 -p kafkaescli.infra kafkaescli.infra
	pyreverse -d ./docs/diagrams --colorized -o "$*" -s 1 -p kafkaescli.interface kafkaescli.interface
	pyreverse -d ./docs/diagrams --colorized -o "$*" -s 1 -p kafkaescli.lib kafkaescli.lib
	sed -i -e 's/set namespaceSeparator none//g' docs/diagrams/classes_*.$*
	rm -fr docs/diagrams/packages_*.$*

py2puml:
	py2puml kafkaescli/domain/ kafkaescli.domain > kafkaescli/kafkaescli.domain.puml
	py2puml kafkaescli/app/ kafkaescli.app > kafkaescli/kafkaescli.app.puml
	py2puml kafkaescli/lib/ kafkaescli.lib > kafkaescli/kafkaescli.lib.puml
	py2puml kafkaescli/interface/ kafkaescli.interface > kafkaescli/kafkaescli.interface.puml

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
	coveralls

pipeline-release.%: pip-install groom diagrams.plantuml diagrams.mmd build
	cd docs/ && $(MAKE) html
	git config --global user.email "ci-build@kafkaescli.pipeline"
	git config --global user.name "ci-build"
	$(MAKE) bump.$*
	poetry publish --username=__token__ --password=$$PYPI_API_TOKEN
