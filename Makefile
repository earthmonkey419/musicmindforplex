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
	@test -x "python" || { echo "Virtual environment missing. Run make install first."; exit 1; }
	@test -f config.py || { echo "config.py missing. Copy config.example.py to config.py and fill in your credentials."; exit 1; }
	"$(VENV)/bin/python" -m web.app
