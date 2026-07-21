import json
from pathlib import Path

import jsonschema
import pytest


ROOT = Path(__file__).resolve().parents[1]
NODE_PATH = ROOT / "data" / "examples" / "double_slit_information.json"
SCHEMA_PATH = ROOT / "schemas" / "node.schema.json"


def test_double_slit_node_matches_schema() -> None:
    node = json.loads(NODE_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    jsonschema.validate(instance=node, schema=schema)
    assert node["status"] == "EST"
    assert node["claims_experimental_verification"] is True


@pytest.mark.parametrize("gamma_abs", [0.0, 0.25, 0.5, 0.8, 1.0])
def test_ideal_visibility_distinguishability_identity(gamma_abs: float) -> None:
    visibility = gamma_abs
    distinguishability = (1.0 - gamma_abs**2) ** 0.5

    assert visibility**2 + distinguishability**2 == pytest.approx(1.0)


def test_remote_trace_preserving_map_does_not_change_local_marginal() -> None:
    # Bell state |Phi+> = (|00> + |11>)/sqrt(2), represented as a density matrix.
    rho_ab = [
        [0.5, 0.0, 0.0, 0.5],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.5, 0.0, 0.0, 0.5],
    ]

    # A dephasing channel on subsystem B removes coherences between B=0 and B=1.
    rho_after = [row[:] for row in rho_ab]
    for i in range(4):
        for j in range(4):
            b_i = i % 2
            b_j = j % 2
            if b_i != b_j:
                rho_after[i][j] = 0.0

    def partial_trace_b(matrix: list[list[float]]) -> list[list[float]]:
        return [
            [sum(matrix[2 * a + b][2 * ap + b] for b in range(2)) for ap in range(2)]
            for a in range(2)
        ]

    assert partial_trace_b(rho_ab) == partial_trace_b(rho_after)
    assert partial_trace_b(rho_after) == [[0.5, 0.0], [0.0, 0.5]]
