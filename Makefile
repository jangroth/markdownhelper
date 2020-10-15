.PHONY: help pipenv check test

help: ## This help
	@grep -E -h "^[a-zA-Z_-]+:.*?## " $(MAKEFILE_LIST) \
	  | sort \
	  | awk -v width=36 'BEGIN {FS = ":.*?## "} {printf "\033[36m%-*s\033[0m %s\n", width, $$1, $$2}'

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

pipenv: ## Install pipenv and dependencies
	pip3 install pipenv
	pipenv install --dev

check: ## Run linters
	flake8
	@echo '*** all checks passing ***'

test: check ## Run tests
	PYTHONPATH=./src/markdownhelper pytest --cov=src --cov-report term-missing
	@echo '*** all tests passing ***'

dist: clean ## builds source and wheel package
	pipenv-setup sync --dev
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist	