import pytest

from upi.constants import C
from upi.dual_observer import (
    Event1D,
    dual_observer_trace,
    lorentz_factor,
    lorentz_transform_event,
    minkowski_interval_m2,
    trace_integrity_rate,
    trace_integrity_ratio,
)


def test_lorentz_profile_preserves_interval_and_round_trip() -> None:
    event_a = Event1D(time_s=2e-6, position_m=300.0)
    result = dual_observer_trace(
        event_a,
        0.6 * C,
        time_tolerance_s=1e-9,
        position_tolerance_m=0.1,
    )

    assert result.gamma == pytest.approx(1.25)
    assert result.predicted_b.time_s == pytest.approx(1.7494807858041578e-6)
    assert result.predicted_b.position_m == pytest.approx(-74.688687)
    assert result.reconstructed_a.time_s == pytest.approx(event_a.time_s)
    assert result.reconstructed_a.position_m == pytest.approx(event_a.position_m)
    assert result.invariant_b_m2 == pytest.approx(result.invariant_a_m2)
    assert result.r0_tir < 1e-10


def test_observation_bias_breaks_trace_and_invariant() -> None:
    event_a = Event1D(time_s=2e-6, position_m=300.0)
    predicted_b = lorentz_transform_event(event_a, 0.6 * C)
    observed_b = Event1D(
        time_s=predicted_b.time_s + 2e-9,
        position_m=predicted_b.position_m + 0.25,
    )
    result = dual_observer_trace(
        event_a,
        0.6 * C,
        observed_b=observed_b,
        time_tolerance_s=1e-9,
        position_tolerance_m=0.1,
    )

    assert result.time_error_s == pytest.approx(3.125432678496633e-9)
    assert result.position_error_m == pytest.approx(0.7621886869999344)
    assert result.r0_tir == pytest.approx(1.0)
    assert result.invariant_relative_error == pytest.approx(0.002467285898080553)


def test_trace_integrity_ratio_clips_each_component() -> None:
    assert trace_integrity_ratio((0.5, 4.0), (1.0, 2.0)) == pytest.approx(0.75)


def test_trace_integrity_rate() -> None:
    assert trace_integrity_rate(0.2, 0.5, 0.25) == pytest.approx(1.2)


def test_invalid_beta_is_rejected() -> None:
    with pytest.raises(ValueError, match=r"\|beta\| < 1"):
        lorentz_factor(1.0)


def test_minkowski_interval_numeric_value() -> None:
    event = Event1D(time_s=2e-6, position_m=300.0)
    assert minkowski_interval_m2(event) == pytest.approx(269502.0714947271)
