.PHONY: help run fixtures demo test lint
help: ## list targets
	@grep -E '^[a-z-]+:.*##' Makefile | sed 's/:.*##/ —/'
run: ## web demo on :8790
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8790
fixtures: ## regenerate the synthetic personal screens
	uv run python bin/make_fixtures.py
demo: ## CLI over every fixture (integration)
	uv run python -m cli.main fixtures/*.png
integration: demo
test: ## unit tests (no model)
	uv run pytest -q
lint:
	uvx ruff check .
