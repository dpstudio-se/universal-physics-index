"""Universal Physics Index (UPI) - machine-readable scientific knowledge graph."""

__version__ = "0.1.0-alpha"
__author__ = "UPI Contributors"
__license__ = "MIT"

from .constants import (
    H, C, K_B, E, N_A,
    N8_REFERENCE_HZ,
    EPSILON_Z_DEFAULT,
    AMPLITUDE_TOLERANCE_DEFAULT,
    PHASE_TOLERANCE_DEFAULT,
)

from .models import (
    Address,
    Quantity,
    EvidenceRecord,
    ScientificStatus,
    EdgeType,
    PhysicsNode,
    Bridge,
    TheoryNode,
    RuntimeMatchResult,
)

from .physics import (
    energy_from_frequency,
    mass_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    index8_from_mass,
    relativistic_total_frequency,
    normalize_signal,
    signal_match,
    complex_signal_match,
)

from .runtime import (
    RuntimeProfile,
    RuntimeProfileLoader,
    get_runtime_loader,
    register_profile,
    activate_profile,
    deactivate_profile,
    get_active_profiles,
)

from .graph import UPIGraph

from .validation import (
    validate_json_schema,
    validate_node_status,
    validate_bridge_consistency,
    validate_status_enum,
    validate_node_json,
    validate_bridge_json,
)

__all__ = [
    # Version
    "__version__",
    # Constants
    "H", "C", "K_B", "E", "N_A",
    "N8_REFERENCE_HZ",
    "EPSILON_Z_DEFAULT",
    "AMPLITUDE_TOLERANCE_DEFAULT",
    "PHASE_TOLERANCE_DEFAULT",
    # Models
    "Address",
    "Quantity",
    "EvidenceRecord",
    "ScientificStatus",
    "EdgeType",
    "PhysicsNode",
    "Bridge",
    "TheoryNode",
    "RuntimeMatchResult",
    # Physics
    "energy_from_frequency",
    "mass_from_frequency",
    "frequency_from_mass",
    "index8_from_frequency",
    "index8_from_mass",
    "relativistic_total_frequency",
    "normalize_signal",
    "signal_match",
    "complex_signal_match",
    # Runtime
    "RuntimeProfile",
    "RuntimeProfileLoader",
    "get_runtime_loader",
    "register_profile",
    "activate_profile",
    "deactivate_profile",
    "get_active_profiles",
    # Graph
    "UPIGraph",
    # Validation
    "validate_json_schema",
    "validate_node_status",
    "validate_bridge_consistency",
    "validate_status_enum",
    "validate_node_json",
    "validate_bridge_json",
]
