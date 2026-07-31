"""Generic UPI transformation engine.

Domain modules provide operators and feedback logic; the core remains domain neutral.
Classification: DER architecture proposal.
"""

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class TransformationState:
    """Generic state container shared by UPI domains."""

    value: Any
    metadata: dict[str, Any] | None = None


class TransformationEngine:
    """Execute a domain supplied transformation with feedback.

    The engine does not contain biological, mechanical, or AI-specific rules.
    Those belong to modules consuming this core.
    """

    def transform(
        self,
        state: TransformationState,
        operator: Callable[[Any], Any],
        feedback: Callable[[Any], Any] | None = None,
    ) -> TransformationState:
        result = operator(state.value)

        if feedback is not None:
            result = feedback(result)

        return TransformationState(
            value=result,
            metadata=state.metadata,
        )
