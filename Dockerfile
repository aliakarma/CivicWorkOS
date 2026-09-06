# CivicWorkOS is a library + CLI scripts, not a hosted service (the
# paper specifies no API, database, or message broker -- see
# docs/paper_implementation_mapping.md). A single lightweight image is
# therefore sufficient; no docker-compose / multi-service stack is
# warranted.
FROM python:3.11-slim

WORKDIR /app

# System dependency for PuLP's bundled CBC solver to run correctly on
# Debian slim images.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml requirements.txt ./
COPY src/ src/
COPY sim/ sim/
COPY scripts/ scripts/
COPY configs/ configs/

RUN pip install --no-cache-dir -e .

# Default action: run the repository's ground-truth check. Override with
# `docker run civicworkos python scripts/run_simulation.py ...` etc.
ENTRYPOINT ["python", "scripts/verify_worked_example.py"]
