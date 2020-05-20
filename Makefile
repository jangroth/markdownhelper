.PHONY: help pipenv check test

help: ## This help
	@grep -E -h "^[a-zA-Z_-]+:.*?## " $(MAKEFILE_LIST) \
	  | sort \
	  | awk -v width=36 'BEGIN {FS = ":.*?## "} {printf "\033[36m%-*s\033[0m %s\n", width, $$1, $$2}'

pipenv: ## Install pipenv and dependencies
	pip3 install pipenv
	pipenv install --dev

check: ## Run linters
	flake8
	@echo '*** all checks passing ***'

test: check ## Run tests
	PYTHONPATH=./src/markdownhelper pytest --cov=src --cov-report term-missing
	@echo '*** all tests passing ***'