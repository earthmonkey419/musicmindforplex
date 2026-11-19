.PHONY: help init install install-full run

UV ?= uv
EXTRA ?= slim

help:
	@echo "make install       Create a virtual environment and install the slim variant"
	@echo "make install-full  Install the TensorFlow variant"
	@echo "make run           Start the web app at http://localhost:8787"

init:
	@command -v $(UV) >/dev/null || { echo "uv is required; install it from https://docs.astral.sh/uv/"; exit 1; }

install: init
	$(UV) sync --extra $(EXTRA)

install-full: EXTRA = full
install-full: install

run: install
	@test -f config.py || { echo "config.py missing. Copy config.example.py to config.py and fill in your credentials."; exit 1; }
	$(UV) run --no-sync python -m web.app
