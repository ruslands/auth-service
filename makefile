export PYTHONPATH := $(PYTHONPATH):$(PWD)

.PHONY: g
g:
	git add --all
	git commit -m "x"
	git push

.PHONY: test.max
test.max:
	pytest --testing=max tests/api/


.PHONY: test.min
test.min:
	pytest --testing=min tests/api/


.PHONY: test
test:
	pytest tests/api/

.PHONY: test.file
test.file:
	pytest tests/api/$(TEST_FILE)

.PHONY: mypy.file
mypy.file:
	mypy $(TEST_FILE) --ignore-missing-imports --follow-imports=skip

.PHONY: migration.auto
migration.auto:
	alembic revision --autogenerate -m ${name}

.PHONY: migration.manual
migration.manual:
	alembic revision -m ${name}

.PHONY: migrate
migrate:
	alembic upgrade head

.PHONY: migration.history
migration.history:
	alembic history

.PHONY: migration.downgrade
migration.downgrade:
	alembic downgrade ${revision}

.PHONY: load_dump
load_dump:
	@sh -c ' \
	if [ -z "$$DUMP_FILE" ] || [ ! -f "$$DUMP_FILE" ]; \
	then \
		echo "DUMP_FILE is not set or does not exist. Using default."; \
		DUMP_FILE="/builds/rtk/backend/data/source_schema.sql"; \
	fi;\
	if [ "$${DUMP_FILE##*.}" = "gz" ]; \
	then \
		echo "Unzipping gzipped dump file..."; \
		gunzip -k -f $$DUMP_FILE; \
		DUMP_FILE=$${DUMP_FILE%.gz}; \
	fi; \
	export PGPASSWORD=$$POSTGRES_PASSWORD; \
	psql -h $$POSTGRES_HOST -U $$POSTGRES_USER -d $$POSTGRES_DB -a -f $$DUMP_FILE > /dev/null'


.PHONY: stamp
stamp:
	alembic stamp base

.PHONY: s3_migrate
s3_migrate:
	python s3_migrations/migrate.py

.PHONY: isort
isort:
	poetry run isort --recursive --verbose .

.PHONY: isort.check
isort.check:
	poetry run isort --recursive . --diff --check-only

.PHONY: ruff
ruff:
	ruff app/ core/ tests/ --verbose

.PHONY: ruff.check
ruff.check:
	poetry run ruff app/ core/ tests/ --diff

.PHONY: black
black:
	poetry run black app/ core/ tests/ --verbose

.PHONY: black.check
black.check:
	poetry run black app/ core/ tests/ --check --extend-exclude builds
