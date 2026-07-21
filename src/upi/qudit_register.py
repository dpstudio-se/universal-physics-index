"""Local generalized qudit gates for mixed-radix torus registers."""

from collections.abc import Sequence
from math import cos, isfinite, pi, prod, sin

from .qudit import QuditState, coordinates_to_index, index_to_coordinates


def _validate_register(
    state: QuditState,
    dimensions: Sequence[int],
    axis: int,
) -> tuple[int, ...]:
    dims = tuple(dimensions)
    if not dims:
        raise ValueError("at least one torus dimension is required")
    for dimension in dims:
        if isinstance(dimension, bool) or not isinstance(dimension, int):
            raise TypeError("dimensions must be integers")
        if dimension < 2:
            raise ValueError("each torus dimension must be at least two")
    if prod(dims) != state.dimension:
        raise ValueError("register dimensions do not match state dimension")
    if len(state.amplitudes) != state.dimension:
        raise ValueError("amplitude count must equal state dimension")
    if abs(sum(abs(value) ** 2 for value in state.amplitudes) - 1.0) > 1e-10:
        raise ValueError("state amplitudes must be normalized")
    if any(
        not isfinite(value.real) or not isfinite(value.imag)
        for value in state.amplitudes
    ):
        raise ValueError("amplitudes must be finite")
    if isinstance(axis, bool) or not isinstance(axis, int):
        raise TypeError("axis must be an integer")
    if not 0 <= axis < len(dims):
        raise ValueError("axis is outside the torus register")
    return dims


def local_shift_gate(
    state: QuditState,
    dimensions: Sequence[int],
    axis: int,
    shift: int = 1,
) -> QuditState:
    """Apply generalized X_d^shift to one selected torus axis."""
    dims = _validate_register(state, dimensions, axis)
    if isinstance(shift, bool) or not isinstance(shift, int):
        raise TypeError("shift must be an integer")
    output = [0j] * state.dimension
    for index, amplitude in enumerate(state.amplitudes):
        coordinates = list(index_to_coordinates(index, dims))
        coordinates[axis] = (coordinates[axis] + shift) % dims[axis]
        output[coordinates_to_index(coordinates, dims)] = amplitude
    return QuditState(state.dimension, tuple(output))


def local_phase_gate(
    state: QuditState,
    dimensions: Sequence[int],
    axis: int,
    power: int = 1,
) -> QuditState:
    """Apply generalized Z_d^power to one selected torus axis."""
    dims = _validate_register(state, dimensions, axis)
    if isinstance(power, bool) or not isinstance(power, int):
        raise TypeError("power must be an integer")
    output: list[complex] = []
    for index, amplitude in enumerate(state.amplitudes):
        coordinate = index_to_coordinates(index, dims)[axis]
        angle = 2.0 * pi * power * coordinate / dims[axis]
        output.append(amplitude * complex(cos(angle), sin(angle)))
    return QuditState(state.dimension, tuple(output))
