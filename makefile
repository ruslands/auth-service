# include ../config/.env # for local development
# export YC_SECRET_ID=<secret id> # for local development

export PYTHONPATH := $(PYTHONPATH):$(PWD)
export YC_SECRET_ID := $(YC_SECRET_ID)
export YC_AUTHORIZED_KEY_ID := $(YC_AUTHORIZED_KEY_ID)
export YC_SERVICE_ACCOUNT_ID := $(YC_SERVICE_ACCOUNT_ID)
export YC_PRIVATE_KEY := $(YC_PRIVATE_KEY)

$(info YC_SECRET_ID is $(YC_SECRET_ID))
$(info YC_AUTHORIZED_KEY_ID is $(YC_AUTHORIZED_KEY_ID))
$(info YC_SERVICE_ACCOUNT_ID is $(YC_SERVICE_ACCOUNT_ID))
$(info YC_PRIVATE_KEY is $(YC_PRIVATE_KEY))

.PHONY: g
g:
	git add --all
	git commit -m "x"
	git push

.PHONY: lint
lint:
	ruff app/ core/ tests/ --verbose


.PHONY: test
test:
	pytest


.PHONY: migration
migration:
	alembic revision --autogenerate -m ${name}


.PHONY: migration.manual
migration.manual:
	alembic revision -m ${name}


.PHONY: migrate
migrate:
	alembic upgrade head


.PHONY: downgrade
downgrade:
	alembic downgrade base


.PHONY: stamp
stamp:
	alembic stamp base
