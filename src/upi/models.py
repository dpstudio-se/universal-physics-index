"""Typed node and bridge models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Status(str, Enum):
    EST = "EST"
    DER = "DER"
    HYP = "HYP"
    STOP = "STOP"
    ERR = "ERR"
    SYM = "SYM"


@dataclass(frozen=True, slots=True)
class Address:
    domain: str
    generation: str
    torus: str
    node: str

    def canonical(self) -> str:
        return f"UPI<{self.domain},{self.generation},{self.torus},{self.node}>"


@dataclass(slots=True)
class PhysicsNode:
    address: Address
    title: str
    status: Status
    quantities: dict[str, Any] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    confusion_guard: list[str] = field(default_factory=list)
    stop_reason: str | None = None
