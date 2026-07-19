"""Typed data models for UPI: nodes, bridges, quantities, and records."""

from dataclasses import dataclass, field
from enum import Enum


class ScientificStatus(str, Enum):
    """Scientific status labels for nodes and bridges.

    EST = established within the declared scientific domain
    DER = derived from explicitly declared assumptions
    HYP = falsifiable but unverified hypothesis
    STOP = missing proof, mechanism, evidence, or selection rule
    ERR = contradicted, invalid, or superseded
    SYM = symbolic or conceptual interpretation only
    """
    EST = "EST"
    DER = "DER"
    HYP = "HYP"
    STOP = "STOP"
    ERR = "ERR"
    SYM = "SYM"


class InformationLayer(str, Enum):
    """Disclosure/formality context; never a scientific evidence rank."""

    PRIVATE = "PRIVATE"
    PUBLIC = "PUBLIC"
    ACADEMIC = "ACADEMIC"


class VerificationType(str, Enum):
    """What kind of check or observation supports a record."""

    SOFTWARE_TEST = "software_test"
    SIMULATION = "simulation"
    MATHEMATICAL_CHECK = "mathematical_check"
    EXPERIMENTAL_OBSERVATION = "experimental_observation"
    REPLICATION = "replication"
    NONE = "none"


class EdgeType(str, Enum):
    """Typed graph relations for bridges."""
    DERIVED_FROM = "DERIVED_FROM"
    CAUSES = "CAUSES"
    DUAL_TO = "DUAL_TO"
    EQUIVALENT_WITHIN = "EQUIVALENT_WITHIN"
    COARSE_GRAINS_TO = "COARSE_GRAINS_TO"
    COMPACTIFIES_TO = "COMPACTIFIES_TO"
    EMERGES_AS = "EMERGES_AS"
    FORM_SIMILAR = "FORM_SIMILAR"
    TOPOLOGY_SHARED = "TOPOLOGY_SHARED"
    MECHANISM_SHARED = "MECHANISM_SHARED"
    CANDIDATE_BRIDGE = "CANDIDATE_BRIDGE"
    CONTRADICTS = "CONTRADICTS"
    STOPS_AT = "STOPS_AT"
    REPRESENTS = "REPRESENTS"
    MEASURED_BY = "MEASURED_BY"
    FALSIFIED_BY = "FALSIFIED_BY"


@dataclass
class Address:
    """UPI address: UPI<D,G,T,N>.

    D = Domain (e.g., physics, mathematics, chemistry)
    G = Generation or derivation lineage
    T = Torus (complete feedback-bounded system)
    N = Node identifier
    """
    domain: str
    generation: int
    torus: str
    node: str

    def __str__(self) -> str:
        """Return string representation: UPI<D,G,T,N>."""
        return f"UPI<{self.domain},{self.generation},{self.torus},{self.node}>"

    @classmethod
    def from_string(cls, s: str) -> "Address":
        """Parse UPI address string."""
        if not s.startswith("UPI<") or not s.endswith(">"):
            raise ValueError(f"Invalid UPI address format: {s}")
        inner = s[4:-1]
        parts = inner.split(",")
        if len(parts) != 4:
            raise ValueError(f"Address must have 4 parts, got {len(parts)}")
        domain, gen_str, torus, node = parts
        try:
            generation = int(gen_str)
        except ValueError:
            raise ValueError(f"Generation must be an integer, got {gen_str}") from None
        return cls(domain, generation, torus, node)


@dataclass
class Quantity:
    """A physical or mathematical quantity."""
    name: str
    value: float
    unit: str
    uncertainty: float | None = None
    reference: str | None = None


@dataclass
class EvidenceRecord:
    """Record of evidence supporting or refuting a claim."""
    type: str  # e.g., "experiment", "observation", "calculation"
    source: str
    date: str | None = None
    confidence: float | None = None  # 0.0 to 1.0
    notes: str | None = None


@dataclass
class PhysicsNode:
    """A node in the UPI graph representing a physical or mathematical concept."""
    address: Address
    title: str
    description: str
    status: ScientificStatus
    quantities: list[Quantity] = field(default_factory=list)
    definitions: list[str] = field(default_factory=list)
    equations: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    mechanism: str | None = None
    evidence: list[EvidenceRecord] = field(default_factory=list)
    primary_sources: list[str] = field(default_factory=list)
    predictions: list[str] = field(default_factory=list)
    falsification_conditions: list[str] = field(default_factory=list)
    information_layer: InformationLayer = InformationLayer.PRIVATE
    reference_frame: str | None = None
    normalization_method: str | None = None
    normalization_claim: str | None = None
    null_model: str | None = None
    control_condition: str | None = None
    statistical_method: str | None = None
    confounders: list[str] = field(default_factory=list)
    replication_rule: str | None = None
    causal_claim: bool = False
    causal_test_method: str | None = None
    verification_type: VerificationType = VerificationType.NONE
    claims_experimental_verification: bool = False
    confusion_guard: str | None = None
    stop_reason: str | None = None  # Required if status == STOP
    tags: list[str] = field(default_factory=list)
    version: str = "0.1.0"
    created_at: str | None = None
    updated_at: str | None = None

    def validate(self) -> list[str]:
        """Validate node consistency. Returns list of error strings."""
        errors = []
        if self.status == ScientificStatus.STOP and not self.stop_reason:
            errors.append("STOP nodes must have stop_reason")
        if not self.address.node:
            errors.append("Node identifier cannot be empty")
        if not self.title:
            errors.append("Title cannot be empty")
        # Local import avoids a module cycle while keeping the model's public
        # validation path consistent with JSON and graph validation.
        from .validation import validate_scientific_boundaries

        errors.extend(validate_scientific_boundaries(self))
        return errors


@dataclass
class Bridge:
    """A directed edge connecting two nodes with a typed relation."""
    source: Address
    target: Address
    relation: EdgeType
    equations: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    mechanism: str | None = None
    evidence: list[EvidenceRecord] = field(default_factory=list)
    status: ScientificStatus = ScientificStatus.HYP
    confusion_guard: str | None = None
    stop_reason: str | None = None
    version: str = "0.1.0"
    created_at: str | None = None
    updated_at: str | None = None

    def validate(self) -> list[str]:
        """Validate bridge consistency. Returns list of error strings."""
        errors = []
        if not self.relation:
            errors.append("Bridge must have relation type")
        if self.status == ScientificStatus.STOP and not self.stop_reason:
            errors.append("STOP bridges must have stop_reason")
        return errors


@dataclass
class TheoryNode:
    """A high-level theory grouping multiple physics nodes."""
    address: Address
    title: str
    description: str
    status: ScientificStatus
    domain: str
    scope: str  # e.g., "classical", "quantum", "relativistic"
    key_concepts: list[str] = field(default_factory=list)
    fundamental_equations: list[str] = field(default_factory=list)
    scope_limits: str | None = None
    related_theories: list[Address] = field(default_factory=list)
    version: str = "0.1.0"
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class RuntimeMatchResult:
    """Result of runtime signal matching operation Z(t,x) = z(t,x) / z_ref(t,x)."""
    normalized_value: float
    observed: float
    reference: float
    epsilon: float
    matches: bool  # abs(Z - 1) <= epsilon
    error: float  # abs(normalized_value - 1)
    profile_active: str | None = None
    notes: str | None = None
