"""Typed scientific records for Universal Physics Index."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
from enum import Enum
from typing import Any, cast


class Status(str, Enum):
    """Scientific classification of a record."""

    EST = "EST"
    DER = "DER"
    HYP = "HYP"
    STOP = "STOP"
    ERR = "ERR"
    SYM = "SYM"


class EvidenceLevel(str, Enum):
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CONSENSUS = "consensus"


class FrequencyType(str, Enum):
    PHOTON = "photon_frequency"
    ANGULAR = "angular_frequency"
    OSCILLATION = "oscillation_frequency"
    SAMPLING = "sampling_frequency"
    REPETITION = "repetition_rate"
    RESONANCE = "resonance_frequency"
    CARRIER = "carrier_frequency"
    BIOLOGICAL = "biological_rhythm"
    SYMBOLIC = "symbolic_reference_frequency"
    NORMALIZATION = "numerical_normalization_frequency"
    REST_MASS = "rest_mass_frequency"


class SourceStatus(str, Enum):
    PEER_REVIEWED = "peer_reviewed"
    PREPRINT = "preprint"
    DATASET = "dataset"
    TEXTBOOK = "textbook"
    STANDARD = "standard"
    OFFICIAL_DOCUMENT = "official_document"
    PERSONAL_NOTE = "personal_note"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Address:
    domain: str
    generation: str
    torus: str
    node: str

    def canonical(self) -> str:
        return f"UPI<{self.domain},{self.generation},{self.torus},{self.node}>"


@dataclass(slots=True)
class Quantity:
    nominal_value: float
    unit: str
    frequency_type: FrequencyType | None = None
    standard_uncertainty: float | None = None
    confidence_interval: tuple[float, float] | None = None
    uncertainty_type: str | None = None
    measurement_method: str | None = None
    sample_size: int | None = None
    source: str | None = None


@dataclass(slots=True)
class Provenance:
    source_type: str
    source_status: SourceStatus = SourceStatus.UNKNOWN
    author: str | None = None
    doi: str | None = None
    arxiv_id: str | None = None
    url: str | None = None
    citation: str | None = None
    dataset_id: str | None = None
    git_commit: str | None = None
    publication_date: str | None = None
    retrieval_date: str | None = None
    page_reference: str | None = None
    source_hash: str | None = None


@dataclass(slots=True)
class AuditEvent:
    event_id: str
    timestamp: str
    node_id: str
    event_type: str
    actor: str
    reason: str
    previous_hash: str | None = None
    current_hash: str | None = None
    warning: str | None = None
    validation_result: str | None = None


@dataclass(slots=True)
class PhysicsNode:
    address: Address
    title: str
    description: str
    scientific_domain: str
    status: Status
    schema_version: str = "0.1.0"
    equation: str | None = None
    variables: dict[str, str] = field(default_factory=dict)
    quantities: dict[str, Quantity] = field(default_factory=dict)
    assumptions: list[str] = field(default_factory=list)
    evidence_level: EvidenceLevel = EvidenceLevel.NONE
    provenance: list[Provenance] = field(default_factory=list)
    references: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    parent_ids: list[str] = field(default_factory=list)
    child_ids: list[str] = field(default_factory=list)
    supersedes: list[str] = field(default_factory=list)
    superseded_by: list[str] = field(default_factory=list)
    evidence_links: list[str] = field(default_factory=list)
    normalization_method: str | None = None
    uncertainty: str | None = None
    test_method: str | None = None
    predicted_observation: str | None = None
    falsification_condition: str | None = None
    required_dataset: str | None = None
    measurable_variable: str | None = None
    testability: str | None = None
    symbolic_interpretation: str | None = None
    notes: list[str] = field(default_factory=list)
    confusion_guard: list[str] = field(default_factory=list)
    stop_reason: str | None = None
    source_hashes: list[str] = field(default_factory=list)
    revision_history: list[AuditEvent] = field(default_factory=list)
    created_date: str = field(default_factory=lambda: date.today().isoformat())
    revised_date: str = field(default_factory=lambda: date.today().isoformat())

    @property
    def identifier(self) -> str:
        return self.address.canonical()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible dictionary."""
        return cast(dict[str, Any], _json_value(asdict(self)))


def _json_value(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, dict):
        return {key: _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value
