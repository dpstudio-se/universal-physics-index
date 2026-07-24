import pytest
from vrasi_qudit import (
    basis_state,
    dual_round_trip_error,
    fourier_transform,
    index_to_coordinates,
    local_fourier_transform,
    local_phase_gate,
    local_shift_gate,
    search_torus_register,
    shift_gate,
    tensor_product,
)


def test_standalone_five_state_qudit_round_trip() -> None:
    state = basis_state(5, 4)
    assert shift_gate(state, 1).probabilities[0] == pytest.approx(1.0)

    reconstructed = fourier_transform(
        fourier_transform(state),
        inverse=True,
    )
    assert reconstructed.amplitudes == pytest.approx(state.amplitudes, abs=1e-12)


def test_standalone_local_torus_functions() -> None:
    dimensions = (4, 5)
    state = tensor_product((basis_state(4, 1), basis_state(5, 2)))

    shifted = local_shift_gate(state, dimensions, axis=0, shift=2)
    shifted_index = max(range(shifted.dimension), key=shifted.probabilities.__getitem__)
    assert index_to_coordinates(shifted_index, dimensions) == (3, 2)

    phased = local_phase_gate(shifted, dimensions, axis=1, power=2)
    assert phased.probabilities == pytest.approx(shifted.probabilities)

    reconstructed = local_fourier_transform(phased, dimensions, axis=0)
    reconstructed = local_fourier_transform(
        reconstructed,
        dimensions,
        axis=0,
        inverse=True,
    )
    assert reconstructed.amplitudes == pytest.approx(phased.amplitudes, abs=1e-12)


def test_standalone_multi_torus_search() -> None:
    result = search_torus_register((4, 5), (7,))

    assert result.total_states == 20
    assert result.success_probability > 0.99
    assert result.ranked_states[0].index == 7
    assert result.ranked_states[0].coordinates == (1, 2)
    assert result.dual_round_trip_error < 1e-12
    assert len(result.stages) > 3


def test_standalone_sparse_duality_invariant() -> None:
    state = basis_state(20, 19)
    assert dual_round_trip_error(state, (4, 5)) < 1e-12
