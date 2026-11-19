.PHONY: help init install install-full run test

help:
	@echo "make install       Create a virtual environment and install all extras"
	@echo "make install-full  Alias for install (includes all extras)"
	@echo "make run           Start the web app at http://localhost:8787"

init:
	@command -v uv >/dev/null || { echo "uv is required. On macOS, install it with: brew install uv"; exit 1; }

install: init
	uv sync --all-extras
	uv lock

install-full: install

run: install
	@test -f config.py || { echo "config.py missing. Copy config.example.py to config.py and fill in your credentials."; exit 1; }
	uv run --no-sync python -m web.app

test: install
	uv run --no-sync coverage run
	uv run --no-sync coverage report
