"""Dual-observer trace metrics with a special-relativistic reference profile.

The Lorentz transformation and Minkowski interval are established physics.
R0_TIR and r0_S are UPI audit metrics built on declared reconstruction
errors and tolerances; they are not new fundamental constants.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable

from .constants import C


@dataclass(frozen=True)
class Event1D:
    """An event in one spatial dimension using SI units."""

    time_s: float
    position_m: float


@dataclass(frozen=True)
class DualObserverTraceResult:
    """Result of a forward Lorentz map and backward reconstruction."""

    observer_a: Event1D
    predicted_b: Event1D
    observed_b: Event1D
    reconstructed_a: Event1D
    relative_velocity_m_s: float
    beta: float
    gamma: float
    invariant_a_m2: float
    invariant_b_m2: float
    invariant_drift_m2: float
    invariant_relative_error: float
    time_error_s: float
    position_error_m: float
    time_tolerance_s: float
    position_tolerance_m: float
    r0_tir: float

    def as_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "observer_a": {
                "time_s": self.observer_a.time_s,
                "position_m": self.observer_a.position_m,
            },
            "predicted_b": {
                "time_s": self.predicted_b.time_s,
                "position_m": self.predicted_b.position_m,
            },
            "observed_b": {
                "time_s": self.observed_b.time_s,
                "position_m": self.observed_b.position_m,
            },
            "reconstructed_a": {
                "time_s": self.reconstructed_a.time_s,
                "position_m": self.reconstructed_a.position_m,
            },
            "relative_velocity_m_s": self.relative_velocity_m_s,
            "beta": self.beta,
            "gamma": self.gamma,
            "omega": {
                "name": "minkowski_interval",
                "invariant_a_m2": self.invariant_a_m2,
                "invariant_b_m2": self.invariant_b_m2,
                "drift_m2": self.invariant_drift_m2,
                "relative_error": self.invariant_relative_error,
            },
            "trace": {
                "time_error_s": self.time_error_s,
                "position_error_m": self.position_error_m,
                "time_tolerance_s": self.time_tolerance_s,
                "position_tolerance_m": self.position_tolerance_m,
                "R0_TIR": self.r0_tir,
            },
        }


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite, got {value}")
    return value


def _validate_event(event: Event1D, name: str) -> None:
    _finite(f"{name}.time_s", event.time_s)
    _finite(f"{name}.position_m", event.position_m)


def lorentz_factor(beta: float) -> float:
    """Return gamma = 1 / sqrt(1 - beta^2) for |beta| < 1."""
    beta = _finite("beta", beta)
    if abs(beta) >= 1.0:
        raise ValueError(f"beta must satisfy |beta| < 1, got {beta}")
    return 1.0 / math.sqrt(1.0 - beta * beta)


def lorentz_transform_event(event: Event1D, relative_velocity_m_s: float) -> Event1D:
    """Map observer A's event into observer B's inertial frame.

    Uses x' = gamma(x - vt) and t' = gamma(t - vx/c^2).
    Positive velocity means B moves in the +x direction relative to A.
    """
    _validate_event(event, "event")
    velocity = _finite("relative_velocity_m_s", relative_velocity_m_s)
    beta = velocity / C
    gamma = lorentz_factor(beta)
    transformed_time = gamma * (event.time_s - velocity * event.position_m / (C * C))
    transformed_position = gamma * (event.position_m - velocity * event.time_s)
    return Event1D(time_s=transformed_time, position_m=transformed_position)


def inverse_lorentz_transform_event(
    event: Event1D, relative_velocity_m_s: float
) -> Event1D:
    """Map observer B's event back into observer A's inertial frame."""
    return lorentz_transform_event(event, -relative_velocity_m_s)


def minkowski_interval_m2(event: Event1D) -> float:
    """Return the invariant interval Omega = (c t)^2 - x^2 in m^2."""
    _validate_event(event, "event")
    return (C * event.time_s) ** 2 - event.position_m**2


def trace_integrity_ratio(errors: Iterable[float], tolerances: Iterable[float]) -> float:
    """Calculate R0_TIR as the mean clipped error-to-tolerance ratio.

    R0_TIR = (1/N) * sum_i min(1, |error_i| / tolerance_i)
    """
    error_values = tuple(float(value) for value in errors)
    tolerance_values = tuple(float(value) for value in tolerances)
    if not error_values:
        raise ValueError("at least one trace component is required")
    if len(error_values) != len(tolerance_values):
        raise ValueError("errors and tolerances must have the same length")

    normalized: list[float] = []
    for index, (error, tolerance) in enumerate(zip(error_values, tolerance_values, strict=True)):
        if not math.isfinite(error):
            raise ValueError(f"error[{index}] must be finite")
        if not math.isfinite(tolerance) or tolerance <= 0.0:
            raise ValueError(f"tolerance[{index}] must be finite and positive")
        normalized.append(min(1.0, abs(error) / tolerance))
    return sum(normalized) / len(normalized)


def trace_integrity_rate(previous_r0_tir: float, current_r0_tir: float, dt_s: float) -> float:
    """Return r0_S = d(R0_TIR)/dt as a finite difference in s^-1."""
    previous = _finite("previous_r0_tir", previous_r0_tir)
    current = _finite("current_r0_tir", current_r0_tir)
    duration = _finite("dt_s", dt_s)
    if not 0.0 <= previous <= 1.0 or not 0.0 <= current <= 1.0:
        raise ValueError("R0_TIR values must be in [0, 1]")
    if duration <= 0.0:
        raise ValueError("dt_s must be positive")
    return (current - previous) / duration


def dual_observer_trace(
    observer_a: Event1D,
    relative_velocity_m_s: float,
    *,
    observed_b: Event1D | None = None,
    time_tolerance_s: float = 1e-9,
    position_tolerance_m: float = 1e-3,
) -> DualObserverTraceResult:
    """Run a Lorentz forward trace, backward reconstruction, and audit score.

    If ``observed_b`` is omitted, the mathematically predicted B state is used.
    Supplying an observed state allows sensor noise or model discrepancy to be
    scored against the declared time and position tolerances.
    """
    _validate_event(observer_a, "observer_a")
    time_tolerance = _finite("time_tolerance_s", time_tolerance_s)
    position_tolerance = _finite("position_tolerance_m", position_tolerance_m)
    if time_tolerance <= 0.0 or position_tolerance <= 0.0:
        raise ValueError("trace tolerances must be positive")

    velocity = _finite("relative_velocity_m_s", relative_velocity_m_s)
    beta = velocity / C
    gamma = lorentz_factor(beta)
    predicted_b = lorentz_transform_event(observer_a, velocity)
    measured_b = predicted_b if observed_b is None else observed_b
    _validate_event(measured_b, "observed_b")
    reconstructed_a = inverse_lorentz_transform_event(measured_b, velocity)

    time_error = reconstructed_a.time_s - observer_a.time_s
    position_error = reconstructed_a.position_m - observer_a.position_m
    r0_tir = trace_integrity_ratio(
        (time_error, position_error),
        (time_tolerance, position_tolerance),
    )

    invariant_a = minkowski_interval_m2(observer_a)
    invariant_b = minkowski_interval_m2(measured_b)
    invariant_drift = invariant_b - invariant_a
    invariant_scale = max(abs(invariant_a), abs(invariant_b), 1.0)
    invariant_relative_error = abs(invariant_drift) / invariant_scale

    return DualObserverTraceResult(
        observer_a=observer_a,
        predicted_b=predicted_b,
        observed_b=measured_b,
        reconstructed_a=reconstructed_a,
        relative_velocity_m_s=velocity,
        beta=beta,
        gamma=gamma,
        invariant_a_m2=invariant_a,
        invariant_b_m2=invariant_b,
        invariant_drift_m2=invariant_drift,
        invariant_relative_error=invariant_relative_error,
        time_error_s=time_error,
        position_error_m=position_error,
        time_tolerance_s=time_tolerance,
        position_tolerance_m=position_tolerance,
        r0_tir=r0_tir,
    )
