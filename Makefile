# Vanna Text2SQL Makefile

.PHONY: install setup start test clean help

help:
	@echo "Available commands:"
	@echo "  install    - Install Python dependencies"
	@echo "  setup      - Set up environment and start services"
	@echo "  start      - Start the API server"
	@echo "  test       - Run tests"
	@echo "  clean      - Clean up temporary files"

install:
	pip install -r requirements.txt

setup:
	cp .env.example .env
	@echo "Please edit .env file with your API keys"
	docker-compose up -d

start:
	python main.py

test:
	python tests/test_simple_fix.py

clean:
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete

dev: install setup start

# Quick development cycle
dev-test: clean test