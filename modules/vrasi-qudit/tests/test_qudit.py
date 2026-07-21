import pytest

from vrasi_qudit import (
    basis_state,
    dual_round_trip_error,
    fourier_transform,
    search_torus_register,
    shift_gate,
)


def test_standalone_five_state_qudit_round_trip() -> None:
    state = basis_state(5, 4)
    assert shift_gate(state, 1).probabilities[0] == pytest.approx(1.0)

    reconstructed = fourier_transform(
        fourier_transform(state),
        inverse=True,
    )
    assert reconstructed.amplitudes == pytest.approx(state.amplitudes, abs=1e-12)


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
