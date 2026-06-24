PYTHON := .venv/bin/python

.PHONY: venv build readme test lint fmt clean

venv:                ## create .venv and install dev dependencies
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

build:               ## render LaTeX templates -> resume/output/
	$(PYTHON) -m resume.builder

readme:              ## refresh the README projects list from resume.yml
	$(PYTHON) -m readme

test:                ## run the test suite
	$(PYTHON) -m pytest -q

lint:                ## ruff lint + format check
	$(PYTHON) -m ruff check .
	$(PYTHON) -m ruff format --check .

fmt:                 ## auto-format and fix with ruff
	$(PYTHON) -m ruff format .
	$(PYTHON) -m ruff check --fix .

clean:               ## remove generated output and caches
	rm -rf resume/output .pytest_cache
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
