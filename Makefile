.PHONY: help run fixtures demo test lint
help: ## list targets
	@grep -E '^[a-z-]+:.*##' Makefile | sed 's/:.*##/ —/'
reset: ## before going on stage: stop the server, forget every consent and ledger entry, start clean
	-lsof -ti :8790 | xargs kill 2>/dev/null; sleep 1
	rm -rf data
	$(MAKE) run
run: ## web demo on :8790
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8790
mcp: ## MCP server over stdio (what `claude mcp add` / Claude Desktop launch)
	uv run python -m app.mcp_server
fixtures: ## regenerate the synthetic personal screens
	uv run python bin/make_fixtures.py
demo: ## CLI over every fixture (integration)
	uv run python -m cli.main fixtures/*.png
integration: demo
test: ## unit tests (no model)
	uv run pytest -q
lint:
	uvx ruff check .
