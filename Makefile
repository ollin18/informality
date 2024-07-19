.PHONY: tests docs

install:
	@echo "Installing..."
	poetry install
	poetry run pre-commit install

activate:
	@echo "Activating virtual environment"
	poetry shell

initialize_git:
	@echo "Initialize git"
	git init

setup: initialize_git install

dependencies:
	@echo "Initializing Git..."
	git init
	@echo "Installing dependencies..."
	poetry install --no-root
	poetry run pre-commit install

env: dependencies
	@echo "Activating virtual environment..."
	poetry shell

tests:
	pytest

docs:
	@echo Save documentation to docs...
	pdoc src -o docs --force
	@echo View API documentation...
	pdoc src --http localhost:8080
