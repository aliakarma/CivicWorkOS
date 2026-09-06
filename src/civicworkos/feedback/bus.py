"""Feedback bus: Paper Sec. 4.1 (Fig. 1), Eq. 20.

"Outcome, incident, appeal, citizen and worker feedback" flows from all
three execution channels (human, AI, robot) to a SINGLE bus that updates
BOTH governance services -- the Civic Capability Ledger and the Policy
Digital Twin. Fig. 1's caption gives the reason this repository preserves
as a structural property, not a convenience: the Ledger holds AI and
robot capability terms that cannot be maintained if machine outcomes
bypass it, and compliance monitoring depends on human outcomes as much
as machine ones. Wiring only one destination, or only human outcomes,
is the specific simplification report Sec. 5.1 warns against.

This is an in-process publish-subscribe implementation (no message
broker) -- the paper names "a publish-subscribe bus" and "event-driven"
architecture (Sec. 4.1) but no technology; report Sec. 17 recommends
"any durable pub/sub with replay" for a production deployment. This
in-process version is the right scope for a reference implementation
and is explicitly NOT durable; see docs/deployment.md.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

Subscriber = Callable[["Outcome"], None]


@dataclass(frozen=True)
class Outcome:
    """One execution-channel outcome, incident, appeal, or feedback event."""

    task_id: str
    domain: str
    service: str
    mode: str
    channel: str  # "human" | "ai" | "robot"
    event_type: str  # "execution_outcome" | "incident" | "appeal" | "citizen_feedback" | "worker_feedback"
    payload: dict[str, Any]
    timestamp: datetime


class FeedbackBus:
    """Publishes Outcome events to every registered subscriber.

    civicworkos.online wires this bus's subscribers to BOTH the ledger's
    and the policy twin's update methods at construction time, so a
    caller cannot accidentally wire only one (the failure mode Fig. 1's
    caption warns against).
    """

    def __init__(self) -> None:
        self._subscribers: list[Subscriber] = []

    def subscribe(self, subscriber: Subscriber) -> None:
        self._subscribers.append(subscriber)

    def emit(self, outcome: Outcome) -> None:
        """Eq. 20: broadcast one outcome to every subscriber."""
        for subscriber in self._subscribers:
            subscriber(outcome)

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)
