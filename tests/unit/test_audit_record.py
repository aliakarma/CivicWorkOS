"""Unit tests for civicworkos.audit.evidentiary_record: Suppl. S1.3."""

from __future__ import annotations

from datetime import datetime

from civicworkos.audit.evidentiary_record import (
    CandidateRecord,
    EvidentiaryRecord,
    EvidentiaryRecordStore,
    RejectionRecord,
)


def _record(task_id="t1", selected_mode="H+R") -> EvidentiaryRecord:
    return EvidentiaryRecord(
        task_id=task_id,
        domain="structural_inspection",
        service="structural_inspection_service",
        d_i=10.0,
        ell_i=8.0,
        drafted_modes=("H", "A", "R", "H+A", "H+R", "A+R", "H+A+R"),
        rejections=(
            RejectionRecord(mode="A", stage="policy_filter", reason="prohibit"),
            RejectionRecord(mode="R", stage="policy_filter", reason="prohibit"),
            RejectionRecord(mode="A+R", stage="policy_filter", reason="prohibit"),
        ),
        candidates=(
            CandidateRecord(mode="H", terms={}, debts={}, cad=0.0, scv=0.294, scv_tilde=0.4937),
            CandidateRecord(mode="H+R", terms={}, debts={}, cad=0.23, scv=0.3539, scv_tilde=0.4937),
        ),
        selected_mode=selected_mode,
        duals_in_force={"lambda_structural_inspection": 0.0250},
        rebalance_timestamp=datetime(2026, 1, 1),
        config_version="v2026-09-01",
        authorizing_panel_decision="PANEL-2026-001",
        accountable_human=None,
    )


def test_content_hash_is_deterministic():
    # decided_at defaults differ between two separately-constructed records
    # (datetime.now(timezone.utc)), so stability is checked on the SAME record object.
    r1 = _record()
    assert r1.content_hash() == r1.content_hash()


def test_content_hash_changes_with_content():
    r1 = _record(selected_mode="H+R")
    r2 = _record(selected_mode="H")
    assert r1.content_hash() != r2.content_hash()


def test_store_is_append_only_and_queryable():
    store = EvidentiaryRecordStore()
    h1 = store.add(_record(task_id="t1"))
    h2 = store.add(_record(task_id="t2"))
    assert h1 != h2
    assert len(store.all()) == 2
    assert len(store.for_task("t1")) == 1
    assert store.for_task("t1")[0].task_id == "t1"


def test_store_has_no_update_or_delete_method():
    store = EvidentiaryRecordStore()
    assert not hasattr(store, "update")
    assert not hasattr(store, "delete")
    assert not hasattr(store, "remove")


def test_replay_validates_against_a_recompute_function():
    store = EvidentiaryRecordStore()
    record = _record(selected_mode="H+R")
    store.add(record)
    assert store.validate_replay(record, recompute_argmax=lambda r: "H+R")
    assert not store.validate_replay(record, recompute_argmax=lambda r: "H")


def test_rejection_records_capture_which_stage_and_reason():
    record = _record()
    policy_rejections = [r for r in record.rejections if r.stage == "policy_filter"]
    assert {r.mode for r in policy_rejections} == {"A", "R", "A+R"}
    assert all(r.reason == "prohibit" for r in policy_rejections)
