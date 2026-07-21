import math

import pytest

from upi import (
    evaluate_coupled_rotors,
    evaluate_helical_motion,
    evaluate_screw_coupling,
    helical_acceleration,
    helical_position,
    helical_velocity,
)


def test_uniform_helix_vectors_and_invariants() -> None:
    position = helical_position(0.0, 0.5, 2.0, 4.0)
    velocity = helical_velocity(0.0, 0.5, 2.0, 4.0)
    acceleration = helical_acceleration(0.0, 0.5, 4.0)

    assert position == pytest.approx((0.0, 0.5, 0.0))
    assert velocity == pytest.approx((2.0, 0.0, 2.0))
    assert acceleration == pytest.approx((0.0, -8.0, 0.0))

    result = evaluate_helical_motion(
        0.5,
        2.0,
        4.0,
        mass_kg=3.0,
        moment_of_inertia_kg_m2=0.25,
        axial_force_n=5.0,
        torque_nm=2.0,
    )
    assert result.tangential_speed_m_s == pytest.approx(2.0)
    assert result.total_speed_m_s == pytest.approx(math.sqrt(8.0))
    assert result.turns_per_second_hz == pytest.approx(2.0 / math.pi)
    assert result.period_s == pytest.approx(math.pi / 2.0)
    assert result.pitch_per_turn_m == pytest.approx(math.pi)
    assert result.reduced_pitch_m_per_rad == pytest.approx(0.5)
    assert result.curvature_per_m == pytest.approx(1.0)
    assert result.torsion_per_m == pytest.approx(1.0)
    assert result.radial_acceleration_m_s2 == pytest.approx(8.0)
    assert result.centripetal_force_n == pytest.approx(24.0)
    assert result.point_kinetic_energy_j == pytest.approx(12.0)
    assert result.rotor_kinetic_energy_j == pytest.approx(2.0)
    assert result.angular_momentum_kg_m2_s == pytest.approx(1.0)
    assert result.axial_power_w == pytest.approx(10.0)
    assert result.rotational_power_w == pytest.approx(8.0)
    assert result.total_power_w == pytest.approx(18.0)
    assert result.helicity_sign == 1


def test_helix_handedness_changes_with_angular_direction() -> None:
    right = evaluate_helical_motion(1.0, 1.0, 2.0)
    left = evaluate_helical_motion(1.0, 1.0, -2.0)

    assert right.curvature_per_m == pytest.approx(left.curvature_per_m)
    assert right.torsion_per_m == pytest.approx(-left.torsion_per_m)
    assert right.helicity_sign == -left.helicity_sign


def test_screw_coupling_conserves_power_with_declared_efficiency() -> None:
    result = evaluate_screw_coupling(
        0.01,
        2.0 * math.pi,
        efficiency=0.8,
        torque_nm=1.0,
    )

    assert result.axial_speed_m_s == pytest.approx(0.01)
    assert result.axial_force_n == pytest.approx(160.0 * math.pi)
    assert result.input_power_w == pytest.approx(2.0 * math.pi)
    assert result.output_power_w == pytest.approx(1.6 * math.pi)
    assert result.dissipated_power_w == pytest.approx(0.4 * math.pi)

    inverse = evaluate_screw_coupling(
        0.01,
        2.0 * math.pi,
        efficiency=0.8,
        axial_force_n=result.axial_force_n,
    )
    assert inverse.torque_nm == pytest.approx(1.0)


def test_counter_rotors_cancel_momentum_but_not_energy() -> None:
    result = evaluate_coupled_rotors(2.0, 3.0, 1.0, -6.0)

    assert result.total_angular_momentum_kg_m2_s == pytest.approx(0.0)
    assert result.total_rotational_energy_j == pytest.approx(27.0)
    assert result.reaction_balance_ratio == pytest.approx(0.0)


def test_helical_models_fail_closed_on_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="angular_speed_rad_s must be non-zero"):
        evaluate_helical_motion(1.0, 1.0, 0.0)
    with pytest.raises(ValueError, match="efficiency must not exceed one"):
        evaluate_screw_coupling(0.01, 1.0, efficiency=1.1, torque_nm=1.0)
    with pytest.raises(ValueError, match="supply exactly one"):
        evaluate_screw_coupling(0.01, 1.0)
    with pytest.raises(ValueError, match="supply exactly one"):
        evaluate_screw_coupling(0.01, 1.0, torque_nm=1.0, axial_force_n=1.0)
