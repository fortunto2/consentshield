.PHONY: help reset run install-mcp mcp fixtures demo integration test lint
help: ## list targets
	@grep -E '^[a-z-]+:.*##' Makefile | sed 's/:.*##/ —/'
reset: ## before going on stage: forget every consent and ledger entry; running servers pick it up, reload the page
	rm -rf data
	@echo "clean. The server on :8790 (if running) re-reads policy on the next request; reload the browser tab."
run: ## web demo on :8790
	uv run uvicorn app.server:app --host 0.0.0.0 --port 8790
install-mcp: ## register the MCP server in Claude Code for every directory (user scope)
	claude mcp add consentshield -s user -- uv run --directory "$(CURDIR)" python -m app.mcp_server
	@echo "done: 'claude mcp list' should show consentshield. Grant Screen Recording to the app that runs Claude."
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
