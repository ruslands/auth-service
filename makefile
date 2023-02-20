g:
	git add --all
	git commit -m "x"
	git push


PYTHON_DIR := ~/.pyenv/versions/3.7.10/bin/python3
VENV = .venv
DB := postgresql://postgres:postgres@localhost/db

CODE = \
    admin \
    api \
    db

JOBS ?= 4

init:
	$(PYTHON_DIR) -m venv .venv
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

lint:
	$(VENV)/bin/black --check $(CODE)
	$(VENV)/bin/flake8 --jobs $(JOBS) --statistics $(CODE)
	$(VENV)/bin/mypy --config-file mypy.ini $(CODE)

pretty:
	$(VENV)/bin/black --target-version py37 --skip-string-normalization $(CODE)
	$(VENV)/bin/isort $(CODE)
	$(VENV)/bin/unify --in-place --recursive $(CODE)
