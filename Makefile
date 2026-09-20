# Every gate step is a target; `make gate` runs them all and stops at the first failure.
UV      ?= uv
RUN     := $(UV) run --frozen
PORT    ?= 8123
export PYTHONPATH := .

.PHONY: install dev lint format typecheck layers test coverage spec-check export-spec spec-diff \
        contract security secrets postman load docker gate

install:
	$(UV) sync --frozen

dev:
	$(RUN) uvicorn app.main:create_app --factory --reload --port 8000

lint:
	$(RUN) ruff check .
	$(RUN) ruff format --check .

format:
	$(RUN) ruff check --fix .
	$(RUN) ruff format .

typecheck:
	$(RUN) mypy --strict app scripts tests

layers:
	$(RUN) lint-imports

test:
	$(RUN) pytest --cov=app --cov-report=term-missing --cov-report=xml

export-spec:
	$(RUN) python scripts/export_openapi.py

spec-check:
	$(RUN) python scripts/export_openapi.py --check

spec-diff:
	$(RUN) python scripts/openapi_diff.py

contract:
	$(RUN) pytest tests/contract -m "contract" -q

security:
	$(RUN) bandit -q -r app -c pyproject.toml
	$(UV) export --frozen --no-dev --no-emit-project -o /tmp/devdash-requirements.txt >/dev/null
	$(RUN) pip-audit -r /tmp/devdash-requirements.txt --no-deps --disable-pip

secrets:
	gitleaks detect --no-banner --redact

postman:
	$(RUN) python scripts/build_postman.py
	./scripts/run_newman.sh $(PORT)

load:
	./scripts/run_load.sh $(PORT)

docker:
	docker build -t devdash-api:local .

gate: lint typecheck layers test spec-check spec-diff contract security postman load
	@echo "GATE PASSED"
