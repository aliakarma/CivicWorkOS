# Inference (Running an Allocation)

"Inference" for CivicWorkOS means running Algorithm 1 — deciding one task's
execution mode. There is no model to load; the "model" is the objective and
constraints themselves, composed from a governance configuration.

## Single-task allocation

```bash
python scripts/run_allocation.py
```

This script:

1. Loads `configs/weights/default.yaml` and
   `configs/domains/structural_inspection.yaml`.
2. Builds a `PolicyDigitalTwin` with the statutory-signoff rule from
   `configs/policy/structural_inspection_signoff.yaml`'s description.
3. Constructs an `AllocationEngine` wired to a `HeuristicMarket`
   ([INVENTED] estimator — see `docs/paper_implementation_mapping.md`).
4. Runs `engine.allocate(task, ...)` on one demo task and prints the
   selected mode, the augmented scores (`SCV~`) for every admissible mode,
   and the evidentiary-record hash.

## Programmatic use

```python
from datetime import date
from civicworkos.online.algorithm1 import AllocationEngine, Duals
from civicworkos.twin.task import TaskProfile
# ... construct policy_twin, market, ledger, hcpb_params, reserve_states,
#     access_constraints, worker_groups, score_weights, debt_weights,
#     audit_store, feedback_bus (see scripts/run_allocation.py for a full example)

engine = AllocationEngine(
    policy_twin=policy_twin, market=market, ledger=ledger,
    hcpb_params=hcpb_params, reserve_states=reserve_states,
    access_constraints=access_constraints, worker_groups=worker_groups,
    score_weights=score_weights, debt_weights=debt_weights,
    duals=Duals(lambda_k={"structural_inspection": 0.0250}),
    audit_store=audit_store, feedback_bus=feedback_bus,
    config_version="v2026-09-01", authorizing_panel_decision="PANEL-2026-001",
)

task = TaskProfile(
    task_id="t1", service="structural_inspection_service", domain="structural_inspection",
    cog=0.55, phy=0.40, emp=0.20, risk=0.30, auth=0.60, priv=0.20, urg=0.40,
    learn=0.60, crit=0.40, duration_hours=6.0,
)
result = engine.allocate(task, date.today(), elapsed_days_in_period=180.0)
print(result.selected_mode, result.is_z4_fallback)
```

`result.evidentiary_record` carries all seven items Suppl. S1.3 requires
(task profile, drafted/surviving modes, per-candidate pricing, admissibility
outcome, duals in force, configuration version, accountable human).

## Where the duals come from

`Duals(lambda_k=..., mu_s=..., nu_kg=...)` should normally be the OUTPUT of
the most recent rebalance (`civicworkos.solver.solve_rebalance`), not a
hand-picked number. See [evaluation.md](evaluation.md) for solving the
city-wide program and extracting fresh duals.

## What "inference" does NOT mean here

There is no forward pass through a neural network, no batch inference
endpoint, and no model checkpoint format. If your use case needs a hosted
HTTP API for allocation decisions, that is a genuine gap this repository
does not fill — see [deployment.md](deployment.md)'s list of what a
production deployment would need beyond what is provided.
