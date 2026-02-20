# Makefile — replaces Maven/Gradle for Python projects.
# Each target = one phase of the CI/CD pipeline.

.PHONY: install test test-unit test-ui run clean monitor monitor-down

## Install all dependencies (BUILD phase)
install:
	pip install -r requirements.txt

## Run only fast unit tests (TEST phase)
test-unit:
	pytest tests/test_calculator.py -v

## Run Selenium UI tests (TEST phase — needs Chrome)
test-ui:
	pytest tests/test_selenium.py -v

## Run all tests
test:
	pytest tests/ -v

## Start the FastAPI app locally (CODE/DEV phase)
run:
	cd src && uvicorn app:app --reload --port 5000

## Start the full monitoring stack: app + Prometheus + Grafana (MONITOR phase)
## Grafana → http://localhost:3000  (admin / admin)
## Prometheus → http://localhost:9090
## App → http://localhost:5000
monitor:
	docker compose up --build -d
	@echo ""
	@echo "Stack is up:"
	@echo "  App        → http://localhost:5001  (Docker; 5000 kept free for make run)"
	@echo "  Metrics    → http://localhost:5001/metrics"
	@echo "  Prometheus → http://localhost:9090"
	@echo "  Grafana    → http://localhost:3000  (admin / admin)"

## Stop and remove all monitoring containers
monitor-down:
	docker compose down

## Remove cached files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; \
	find . -name "*.pyc" -delete 2>/dev/null; \
	rm -rf .pytest_cache; \
	echo "Clean done."
