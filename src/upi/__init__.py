"""Universal Physics Index (UPI) - machine-readable scientific knowledge graph."""

__version__ = "0.1.0-alpha"
__author__ = "UPI Contributors"
__license__ = "MIT"

from .constants import (
    AMPLITUDE_TOLERANCE_DEFAULT,
    EPSILON_Z_DEFAULT,
    K_B,
    N8_REFERENCE_HZ,
    N_A,
    PHASE_TOLERANCE_DEFAULT,
    C,
    E,
    H,
)
from .debug import generate_debug_report, render_debug_markdown
from .graph import UPIGraph
from .models import (
    Address,
    Bridge,
    EdgeType,
    EvidenceRecord,
    InformationLayer,
    PhysicsNode,
    Quantity,
    RuntimeMatchResult,
    ScientificStatus,
    TheoryNode,
    VerificationType,
)
from .physics import (
    complex_signal_match,
    energy_from_frequency,
    frequency_from_mass,
    index8_from_frequency,
    index8_from_mass,
    mass_from_frequency,
    normalize_signal,
    relativistic_total_frequency,
    signal_match,
)
from .runtime import (
    RuntimeProfile,
    RuntimeProfileLoader,
    activate_profile,
    deactivate_profile,
    get_active_profiles,
    get_runtime_loader,
    register_profile,
)
from .validation import (
    validate_bridge_consistency,
    validate_bridge_json,
    validate_json_schema,
    validate_node_json,
    validate_node_status,
    validate_record_boundaries,
    validate_scientific_boundaries,
    validate_status_enum,
)
from .workflow import (
    WorkflowState,
    validate_result,
    validate_task,
    validate_task_result_pair,
    validate_transition,
    validate_workflow,
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
    "InformationLayer",
    "VerificationType",
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
    "generate_debug_report",
    "render_debug_markdown",
    # Declarative workflows
    "WorkflowState",
    "validate_task",
    "validate_result",
    "validate_workflow",
    "validate_transition",
    "validate_task_result_pair",
    # Validation
    "validate_json_schema",
    "validate_node_status",
    "validate_bridge_consistency",
    "validate_status_enum",
    "validate_node_json",
    "validate_bridge_json",
    "validate_scientific_boundaries",
    "validate_record_boundaries",
]
