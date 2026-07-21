"""Classical state-vector simulator for multi-torus qudit search.

The module implements established finite-dimensional quantum mathematics in a
classical digital simulator. It does not claim quantum hardware, coherence, or
quantum speedup.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from math import asin, cos, isfinite, pi, prod, sin, sqrt


@dataclass(frozen=True, slots=True)
class QuditState:
    """Normalized state vector for a finite-dimensional qudit register."""

    dimension: int
    amplitudes: tuple[complex, ...]

    @property
    def probabilities(self) -> tuple[float, ...]:
        return tuple(abs(amplitude) ** 2 for amplitude in self.amplitudes)


@dataclass(frozen=True, slots=True)
class SearchStage:
    """One auditable stage in the digital search pipeline."""

    name: str
    marked_probability: float
    normalization_error: float


@dataclass(frozen=True, slots=True)
class RankedState:
    """One measured basis-state candidate."""

    index: int
    coordinates: tuple[int, ...]
    probability: float


@dataclass(frozen=True, slots=True)
class TorusSearchResult:
    """Result envelope for a multi-torus amplitude-amplification search."""

    dimensions: tuple[int, ...]
    total_states: int
    target_indices: tuple[int, ...]
    iterations: int
    success_probability: float
    dual_round_trip_error: float
    ranked_states: tuple[RankedState, ...]
    stages: tuple[SearchStage, ...]
    model_status: str = "DER"
    verification_type: str = "software_test"
    claims_experimental_verification: bool = False


def _validate_dimension(dimension: int) -> int:
    if isinstance(dimension, bool) or not isinstance(dimension, int):
        raise TypeError("dimension must be an integer")
    if dimension < 2:
        raise ValueError("dimension must be at least two")
    return dimension


def _validate_dimensions(dimensions: Sequence[int]) -> tuple[int, ...]:
    normalized = tuple(_validate_dimension(value) for value in dimensions)
    if not normalized:
        raise ValueError("at least one torus dimension is required")
    return normalized


def _validate_state(state: QuditState) -> QuditState:
    dimension = _validate_dimension(state.dimension)
    if len(state.amplitudes) != dimension:
        raise ValueError("amplitude count must equal state dimension")
    for amplitude in state.amplitudes:
        if not isfinite(amplitude.real) or not isfinite(amplitude.imag):
            raise ValueError("amplitudes must be finite")
    norm = sum(abs(amplitude) ** 2 for amplitude in state.amplitudes)
    if abs(norm - 1.0) > 1e-10:
        raise ValueError("state amplitudes must be normalized")
    return state


def _state_from_amplitudes(amplitudes: Sequence[complex]) -> QuditState:
    values = tuple(complex(value) for value in amplitudes)
    dimension = _validate_dimension(len(values))
    norm = sum(abs(value) ** 2 for value in values)
    if norm <= 0.0 or not isfinite(norm):
        raise ValueError("state norm must be finite and positive")
    scale = sqrt(norm)
    return QuditState(dimension, tuple(value / scale for value in values))


def basis_state(dimension: int, index: int) -> QuditState:
    """Return one computational-basis state |index>."""
    dimension = _validate_dimension(dimension)
    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError("index must be an integer")
    if not 0 <= index < dimension:
        raise ValueError("index is outside the qudit basis")
    amplitudes = [0j] * dimension
    amplitudes[index] = 1.0 + 0j
    return QuditState(dimension, tuple(amplitudes))


def uniform_state(dimension: int) -> QuditState:
    """Return an equal-amplitude state over all basis states."""
    dimension = _validate_dimension(dimension)
    amplitude = 1.0 / sqrt(dimension)
    return QuditState(dimension, tuple(complex(amplitude) for _ in range(dimension)))


def shift_gate(state: QuditState, shift: int = 1) -> QuditState:
    """Apply the generalized Pauli-X cyclic shift X^shift."""
    state = _validate_state(state)
    if isinstance(shift, bool) or not isinstance(shift, int):
        raise TypeError("shift must be an integer")
    output = [0j] * state.dimension
    for index, amplitude in enumerate(state.amplitudes):
        output[(index + shift) % state.dimension] = amplitude
    return QuditState(state.dimension, tuple(output))


def phase_gate(state: QuditState, power: int = 1) -> QuditState:
    """Apply the generalized Pauli-Z phase gate Z^power."""
    state = _validate_state(state)
    if isinstance(power, bool) or not isinstance(power, int):
        raise TypeError("power must be an integer")
    output = []
    for index, amplitude in enumerate(state.amplitudes):
        angle = 2.0 * pi * power * index / state.dimension
        phase = complex(cos(angle), sin(angle))
        output.append(amplitude * phase)
    return QuditState(state.dimension, tuple(output))


def fourier_transform(state: QuditState, *, inverse: bool = False) -> QuditState:
    """Apply the normalized discrete quantum Fourier transform."""
    state = _validate_state(state)
    sign = -1.0 if inverse else 1.0
    scale = 1.0 / sqrt(state.dimension)
    output: list[complex] = []
    for output_index in range(state.dimension):
        total = 0j
        for input_index, amplitude in enumerate(state.amplitudes):
            angle = sign * 2.0 * pi * input_index * output_index / state.dimension
            total += amplitude * complex(cos(angle), sin(angle))
        output.append(scale * total)
    return _state_from_amplitudes(output)


def coordinates_to_index(coordinates: Sequence[int], dimensions: Sequence[int]) -> int:
    """Convert mixed-radix torus coordinates to one flattened basis index."""
    dims = _validate_dimensions(dimensions)
    coords = tuple(coordinates)
    if len(coords) != len(dims):
        raise ValueError("coordinate count must equal torus count")
    index = 0
    for coordinate, dimension in zip(coords, dims, strict=True):
        if isinstance(coordinate, bool) or not isinstance(coordinate, int):
            raise TypeError("coordinates must be integers")
        if not 0 <= coordinate < dimension:
            raise ValueError("coordinate is outside its torus dimension")
        index = index * dimension + coordinate
    return index


def index_to_coordinates(index: int, dimensions: Sequence[int]) -> tuple[int, ...]:
    """Convert one flattened basis index to mixed-radix torus coordinates."""
    dims = _validate_dimensions(dimensions)
    total = prod(dims)
    if isinstance(index, bool) or not isinstance(index, int):
        raise TypeError("index must be an integer")
    if not 0 <= index < total:
        raise ValueError("index is outside the torus register")
    coordinates = [0] * len(dims)
    remainder = index
    for axis in range(len(dims) - 1, -1, -1):
        coordinates[axis] = remainder % dims[axis]
        remainder //= dims[axis]
    return tuple(coordinates)


def tensor_product(states: Sequence[QuditState]) -> QuditState:
    """Return the Kronecker product of one or more qudit states."""
    if not states:
        raise ValueError("at least one state is required")
    amplitudes: tuple[complex, ...] = (1.0 + 0j,)
    for state in states:
        validated = _validate_state(state)
        amplitudes = tuple(
            left * right
            for left in amplitudes
            for right in validated.amplitudes
        )
    return QuditState(len(amplitudes), amplitudes)


def local_fourier_transform(
    state: QuditState,
    dimensions: Sequence[int],
    axis: int,
    *,
    inverse: bool = False,
) -> QuditState:
    """Apply a Fourier transform to one torus while preserving all others."""
    state = _validate_state(state)
    dims = _validate_dimensions(dimensions)
    if prod(dims) != state.dimension:
        raise ValueError("register dimensions do not match state dimension")
    if isinstance(axis, bool) or not isinstance(axis, int):
        raise TypeError("axis must be an integer")
    if not 0 <= axis < len(dims):
        raise ValueError("axis is outside the torus register")

    output = [0j] * state.dimension
    for base_index in range(state.dimension):
        base_coordinates = list(index_to_coordinates(base_index, dims))
        if base_coordinates[axis] != 0:
            continue
        local_amplitudes = []
        local_indices = []
        for coordinate in range(dims[axis]):
            base_coordinates[axis] = coordinate
            local_index = coordinates_to_index(base_coordinates, dims)
            local_indices.append(local_index)
            local_amplitudes.append(state.amplitudes[local_index])
        transformed = fourier_transform(
            _state_from_amplitudes(local_amplitudes),
            inverse=inverse,
        )
        local_norm = sqrt(sum(abs(value) ** 2 for value in local_amplitudes))
        for local_index, amplitude in zip(
            local_indices,
            transformed.amplitudes,
            strict=True,
        ):
            output[local_index] = amplitude * local_norm
    return _state_from_amplitudes(output)


def dual_round_trip_error(state: QuditState, dimensions: Sequence[int]) -> float:
    """Measure reconstruction error after local Fourier duality and inversion."""
    dims = _validate_dimensions(dimensions)
    transformed = _validate_state(state)
    for axis in range(len(dims)):
        transformed = local_fourier_transform(transformed, dims, axis)
    for axis in range(len(dims) - 1, -1, -1):
        transformed = local_fourier_transform(
            transformed,
            dims,
            axis,
            inverse=True,
        )
    return max(
        abs(before - after)
        for before, after in zip(
            state.amplitudes,
            transformed.amplitudes,
            strict=True,
        )
    )


def phase_oracle(state: QuditState, target_indices: Sequence[int]) -> QuditState:
    """Flip the phase of every marked computational-basis state."""
    state = _validate_state(state)
    targets = _validate_targets(target_indices, state.dimension)
    output = list(state.amplitudes)
    for target in targets:
        output[target] *= -1.0
    return QuditState(state.dimension, tuple(output))


def diffusion_operator(state: QuditState) -> QuditState:
    """Reflect amplitudes around their arithmetic mean."""
    state = _validate_state(state)
    mean = sum(state.amplitudes) / state.dimension
    return _state_from_amplitudes(
        tuple(2.0 * mean - amplitude for amplitude in state.amplitudes)
    )


def optimal_search_iterations(total_states: int, marked_states: int) -> int:
    """Return the ideal Grover iteration count for a known marked-state count."""
    if isinstance(total_states, bool) or not isinstance(total_states, int):
        raise TypeError("total_states must be an integer")
    if isinstance(marked_states, bool) or not isinstance(marked_states, int):
        raise TypeError("marked_states must be an integer")
    if total_states < 2:
        raise ValueError("total_states must be at least two")
    if not 1 <= marked_states <= total_states:
        raise ValueError("marked_states must be within the search space")
    theta = asin(sqrt(marked_states / total_states))
    return max(0, round(pi / (4.0 * theta) - 0.5))


def _validate_targets(target_indices: Sequence[int], total_states: int) -> tuple[int, ...]:
    targets = tuple(target_indices)
    if not targets:
        raise ValueError("at least one target state is required")
    if len(set(targets)) != len(targets):
        raise ValueError("target states must be unique")
    for target in targets:
        if isinstance(target, bool) or not isinstance(target, int):
            raise TypeError("target indices must be integers")
        if not 0 <= target < total_states:
            raise ValueError("target index is outside the search space")
    return targets


def _stage(name: str, state: QuditState, targets: tuple[int, ...]) -> SearchStage:
    probabilities = state.probabilities
    return SearchStage(
        name=name,
        marked_probability=sum(probabilities[index] for index in targets),
        normalization_error=abs(sum(probabilities) - 1.0),
    )


def search_torus_register(
    dimensions: Sequence[int],
    target_indices: Sequence[int],
    *,
    iterations: int | None = None,
    top_k: int = 5,
) -> TorusSearchResult:
    """Search a multi-torus qudit register with amplitude amplification.

    The implementation is a classical state-vector simulation. Its memory and
    runtime scale with the complete basis size, so it does not provide physical
    quantum acceleration.
    """
    dims = _validate_dimensions(dimensions)
    total_states = prod(dims)
    if total_states <= 3:
        raise ValueError("the search register must contain more than three states")
    targets = _validate_targets(target_indices, total_states)
    if iterations is None:
        iteration_count = optimal_search_iterations(total_states, len(targets))
    else:
        if isinstance(iterations, bool) or not isinstance(iterations, int):
            raise TypeError("iterations must be an integer")
        if iterations < 0:
            raise ValueError("iterations must be non-negative")
        iteration_count = iterations
    if isinstance(top_k, bool) or not isinstance(top_k, int):
        raise TypeError("top_k must be an integer")
    if top_k < 1:
        raise ValueError("top_k must be positive")

    state = uniform_state(total_states)
    stages = [_stage("initialize_uniform", state, targets)]

    dual_state = state
    for axis in range(len(dims)):
        dual_state = local_fourier_transform(dual_state, dims, axis)
        stages.append(_stage(f"dual_forward_torus_{axis}", dual_state, targets))
    for axis in range(len(dims) - 1, -1, -1):
        dual_state = local_fourier_transform(
            dual_state,
            dims,
            axis,
            inverse=True,
        )
        stages.append(_stage(f"dual_inverse_torus_{axis}", dual_state, targets))

    reconstruction_error = max(
        abs(before - after)
        for before, after in zip(
            state.amplitudes,
            dual_state.amplitudes,
            strict=True,
        )
    )
    state = dual_state

    for iteration in range(iteration_count):
        state = phase_oracle(state, targets)
        stages.append(_stage(f"oracle_{iteration + 1}", state, targets))
        state = diffusion_operator(state)
        stages.append(_stage(f"diffusion_{iteration + 1}", state, targets))

    probabilities = state.probabilities
    ranked_indices = sorted(
        range(total_states),
        key=lambda index: (-probabilities[index], index),
    )[: min(top_k, total_states)]
    ranked_states = tuple(
        RankedState(
            index=index,
            coordinates=index_to_coordinates(index, dims),
            probability=probabilities[index],
        )
        for index in ranked_indices
    )
    stages.append(_stage("ranked_measurement", state, targets))

    return TorusSearchResult(
        dimensions=dims,
        total_states=total_states,
        target_indices=targets,
        iterations=iteration_count,
        success_probability=sum(probabilities[index] for index in targets),
        dual_round_trip_error=reconstruction_error,
        ranked_states=ranked_states,
        stages=tuple(stages),
    )
