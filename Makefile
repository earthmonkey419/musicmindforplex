.PHONY: help install install-full run

help:
	@echo "make install       Create a virtual environment and install the slim variant"
	@echo "make install-full  Install the TensorFlow variant"
	@echo "make run           Start the web app at http://localhost:8787"



init:
	pip install uv

install: init
	uv sync
	uv lock

install-full: EXTRA = full
install-full: install

run: install
	@test -f config.py || { echo "config.py missing. Copy config.example.py to config.py and fill in your credentials."; exit 1; }
	uv run python -m web.app
