"""Typed data models for UPI: nodes, bridges, quantities, and records."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime


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
            raise ValueError(f"Generation must be an integer, got {gen_str}")
        return cls(domain, generation, torus, node)


@dataclass
class Quantity:
    """A physical or mathematical quantity."""
    name: str
    value: float
    unit: str
    uncertainty: Optional[float] = None
    reference: Optional[str] = None


@dataclass
class EvidenceRecord:
    """Record of evidence supporting or refuting a claim."""
    type: str  # e.g., "experiment", "observation", "calculation"
    source: str
    date: Optional[str] = None
    confidence: Optional[float] = None  # 0.0 to 1.0
    notes: Optional[str] = None


@dataclass
class PhysicsNode:
    """A node in the UPI graph representing a physical or mathematical concept."""
    address: Address
    title: str
    description: str
    status: ScientificStatus
    quantities: List[Quantity] = field(default_factory=list)
    definitions: List[str] = field(default_factory=list)
    equations: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    mechanism: Optional[str] = None
    evidence: List[EvidenceRecord] = field(default_factory=list)
    primary_sources: List[str] = field(default_factory=list)
    predictions: List[str] = field(default_factory=list)
    falsification_conditions: List[str] = field(default_factory=list)
    confusion_guard: Optional[str] = None
    stop_reason: Optional[str] = None  # Required if status == STOP
    tags: List[str] = field(default_factory=list)
    version: str = "0.1.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def validate(self) -> List[str]:
        """Validate node consistency. Returns list of error strings."""
        errors = []
        if self.status == ScientificStatus.STOP and not self.stop_reason:
            errors.append("STOP nodes must have stop_reason")
        if not self.address.node:
            errors.append("Node identifier cannot be empty")
        if not self.title:
            errors.append("Title cannot be empty")
        return errors


@dataclass
class Bridge:
    """A directed edge connecting two nodes with a typed relation."""
    source: Address
    target: Address
    relation: EdgeType
    equations: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    mechanism: Optional[str] = None
    evidence: List[EvidenceRecord] = field(default_factory=list)
    status: ScientificStatus = ScientificStatus.HYP
    confusion_guard: Optional[str] = None
    stop_reason: Optional[str] = None
    version: str = "0.1.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def validate(self) -> List[str]:
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
    key_concepts: List[str] = field(default_factory=list)
    fundamental_equations: List[str] = field(default_factory=list)
    scope_limits: Optional[str] = None
    related_theories: List[Address] = field(default_factory=list)
    version: str = "0.1.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class RuntimeMatchResult:
    """Result of runtime signal matching operation Z(t,x) = z(t,x) / z_ref(t,x)."""
    normalized_value: float
    observed: float
    reference: float
    epsilon: float
    matches: bool  # abs(Z - 1) <= epsilon
    error: float  # abs(normalized_value - 1)
    profile_active: Optional[str] = None
    notes: Optional[str] = None
