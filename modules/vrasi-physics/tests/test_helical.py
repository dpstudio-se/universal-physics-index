import math

import pytest
from vrasi_physics import (
    evaluate_coupled_rotors,
    evaluate_helical_motion,
    evaluate_screw_coupling,
    helical_position,
)


def test_standalone_helix_matches_analytic_solution() -> None:
    assert helical_position(0.0, 0.5, 2.0, 4.0) == pytest.approx((0.0, 0.5, 0.0))

    result = evaluate_helical_motion(0.5, 2.0, 4.0)
    assert result.tangential_speed_m_s == pytest.approx(2.0)
    assert result.total_speed_m_s == pytest.approx(math.sqrt(8.0))
    assert result.pitch_per_turn_m == pytest.approx(math.pi)
    assert result.curvature_per_m == pytest.approx(1.0)
    assert result.torsion_per_m == pytest.approx(1.0)
    assert result.radial_acceleration_m_s2 == pytest.approx(8.0)
    assert result.model_status == "EST"
    assert result.claims_experimental_verification is False


def test_standalone_screw_and_counter_rotation() -> None:
    screw = evaluate_screw_coupling(
        0.01,
        2.0 * math.pi,
        efficiency=0.8,
        torque_nm=1.0,
    )
    assert screw.axial_speed_m_s == pytest.approx(0.01)
    assert screw.output_power_w == pytest.approx(0.8 * screw.input_power_w)

    rotors = evaluate_coupled_rotors(2.0, 3.0, 1.0, -6.0)
    assert rotors.total_angular_momentum_kg_m2_s == pytest.approx(0.0)
    assert rotors.total_rotational_energy_j == pytest.approx(27.0)
    assert rotors.reaction_balance_ratio == pytest.approx(0.0)
