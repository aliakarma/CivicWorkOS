"""Calibration sources: Paper sec:protocol, Suppl. Section S4.

"No data from them has yet been retrieved or analyzed for this article"
(Suppl. Table S3 caption). `INTENDED_CALIBRATION_SOURCES` below
documents what the paper NAMES as intended future calibration inputs --
it is metadata, not a data connector, and this repository does not
fetch, cache, or ship any data from these portals.

`synthetic_demo_tasks()` is this repository's OWN synthetic task
generator, used only so the simulation testbed (sim.des) can be smoke-
tested end to end. It has no connection to any of the sources below and
must never be described as calibrated. Every task it returns carries
`is_synthetic_demo_data=True` framing in the surrounding code path.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from civicworkos.twin.task import TaskProfile


@dataclass(frozen=True)
class CalibrationSource:
    name: str
    portal: str
    sector: str
    role: str
    status: str


INTENDED_CALIBRATION_SOURCES: list[CalibrationSource] = [
    CalibrationSource(
        "DSNY monthly tonnage; collection-route and district geography",
        "NYC Open Data", "waste_and_sanitation",
        "Calibrate waste/sanitation task arrivals", "not retrieved (Suppl. S4)",
    ),
    CalibrationSource(
        "TfL performance and ridership releases",
        "London Datastore", "public_transport_operations",
        "Calibrate public-transport operations", "not retrieved (Suppl. S4)",
    ),
    CalibrationSource(
        "311 service requests",
        "NYC Open Data", "citizen_service_administration",
        "Calibrate citizen-service administration arrivals", "not retrieved (Suppl. S4)",
    ),
    CalibrationSource(
        "Incident and service-request series",
        "Open Data BCN", "citizen_service_administration",
        "Calibrate citizen-service administration", "not retrieved (Suppl. S4)",
    ),
    CalibrationSource(
        "Municipal property and building registers",
        "Helsinki Region Infoshare", "municipal_facility_management",
        "Calibrate facility management", "not retrieved (Suppl. S4)",
    ),
    CalibrationSource(
        "Asset condition and inspection-interval records",
        "open portals; national bridge inventories where published",
        "infrastructure_inspection_and_maintenance",
        "Calibrate infrastructure inspection", "not retrieved (Suppl. S4)",
    ),
    CalibrationSource(
        "Establishment / headcount tables",
        "same municipalities", "workforce_composition",
        "Practitioner counts by domain; age and tenure where published",
        "not retrieved (Suppl. S4)",
    ),
    CalibrationSource(
        "Emergency logistics",
        "no comparable open series identified",
        "emergency_logistics",
        "Falls back to fleet-utilization distributions (MeseguerValenzuela2025, Hady2025)",
        "no open source; not retrieved",
    ),
]


def synthetic_demo_tasks(
    n: int,
    domain: str,
    service: str,
    seed: int,
) -> list[TaskProfile]:
    """[SYNTHETIC DEMO DATA -- NOT paper data, NOT calibrated to any source]

    Generates `n` tasks with random [0,1] demand dimensions and a
    duration drawn from a modest range, for smoke-testing the simulation
    pipeline only. `seed` makes generation reproducible run-to-run, which
    is a software-engineering property (deterministic tests), not a
    claim about representativeness of any real task population.
    """
    rng = random.Random(seed)
    tasks = []
    for i in range(n):
        tasks.append(
            TaskProfile(
                task_id=f"{domain}-synthetic-{seed}-{i:05d}",
                service=service,
                domain=domain,
                cog=rng.random(),
                phy=rng.random(),
                emp=rng.random(),
                risk=rng.random(),
                auth=rng.random(),
                priv=rng.random(),
                urg=rng.random(),
                learn=rng.uniform(0.3, 0.9),
                crit=rng.random(),
                duration_hours=rng.uniform(2.0, 12.0),
            )
        )
    return tasks
