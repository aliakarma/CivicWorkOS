.PHONY: install install-dev verify test test-unit test-integration test-smoke lint format typecheck clean run-allocation run-rebalance run-simulation protocol protocol-dev exploratory sensitivity docker-build docker-run

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# The repository's only ground-truth check (report Sec. 7, Phase 0).
# Run this first after any change to civicworkos.scoring, .constraints.hcpb,
# or .analytic.
verify:
	python scripts/verify_worked_example.py

test:
	pytest tests/ -v

test-unit:
	pytest tests/unit -v

test-integration:
	pytest tests/integration -v

test-smoke:
	pytest tests/smoke -v

lint:
	ruff check src/ sim/ scripts/ tests/

format:
	ruff format src/ sim/ scripts/ tests/

typecheck:
	mypy src/civicworkos

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache *.egg-info src/*.egg-info

run-allocation:
	python scripts/run_allocation.py

run-rebalance:
	python scripts/run_rebalance.py 12

run-simulation:
	python scripts/run_simulation.py 200 42

# The article's reference execution: 450 runs on reporting seeds 0-29,
# outputs copied to Paper/Frontiers/data/ (10 to 13 minutes on 12 cores).
protocol:
	python scripts/run_protocol.py --paper
	cd Paper/Frontiers && python make_sim_tables.py --splice && python audit_numbers.py --quiet

# Exploratory analyses added in revision (outcome-only learning ablation,
# sensitivity to tau_ret and machine prices); not in the pre-specified family.
exploratory:
	python scripts/run_exploratory.py

# Development seeds only; never used for reported numbers.
protocol-dev:
	python scripts/run_protocol.py --seeds 1000 1009 --out results/protocol_dev

sensitivity:
	python scripts/sensitivity_sweep.py 2000 0.2

docker-build:
	docker build -t civicworkos .

docker-run:
	docker run --rm civicworkos
