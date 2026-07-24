import math

import pytest

from upi import (
    basis_state,
    coordinates_to_index,
    dual_round_trip_error,
    fourier_transform,
    index_to_coordinates,
    local_fourier_transform,
    local_phase_gate,
    local_shift_gate,
    phase_gate,
    search_torus_register,
    shift_gate,
    tensor_product,
)


def test_five_state_qudit_shift_phase_and_fourier_round_trip() -> None:
    state = basis_state(5, 2)
    shifted = shift_gate(state, 2)
    assert shifted.probabilities == pytest.approx((0.0, 0.0, 0.0, 0.0, 1.0))

    phased = phase_gate(state, 1)
    assert phased.probabilities == pytest.approx(state.probabilities)

    dual = fourier_transform(state)
    reconstructed = fourier_transform(dual, inverse=True)
    assert reconstructed.amplitudes == pytest.approx(state.amplitudes, abs=1e-12)
    assert sum(dual.probabilities) == pytest.approx(1.0)


def test_mixed_radix_torus_coordinates_are_bijective() -> None:
    dimensions = (4, 5, 6)
    for index in range(math.prod(dimensions)):
        coordinates = index_to_coordinates(index, dimensions)
        assert coordinates_to_index(coordinates, dimensions) == index


def test_each_torus_has_local_shift_phase_and_fourier_functions() -> None:
    dimensions = (4, 5)
    state = tensor_product((basis_state(4, 1), basis_state(5, 2)))

    shifted = local_shift_gate(state, dimensions, axis=0, shift=2)
    shifted_index = max(range(shifted.dimension), key=shifted.probabilities.__getitem__)
    assert index_to_coordinates(shifted_index, dimensions) == (3, 2)

    phased = local_phase_gate(shifted, dimensions, axis=1, power=2)
    assert phased.probabilities == pytest.approx(shifted.probabilities)

    dual = local_fourier_transform(phased, dimensions, axis=0)
    reconstructed = local_fourier_transform(
        dual,
        dimensions,
        axis=0,
        inverse=True,
    )
    assert reconstructed.amplitudes == pytest.approx(phased.amplitudes, abs=1e-12)


def test_local_fourier_round_trip_handles_sparse_slices() -> None:
    state = tensor_product((basis_state(4, 3), basis_state(5, 2)))
    dual = local_fourier_transform(state, (4, 5), 0)
    dual = local_fourier_transform(dual, (4, 5), 1)
    reconstructed = local_fourier_transform(dual, (4, 5), 1, inverse=True)
    reconstructed = local_fourier_transform(
        reconstructed,
        (4, 5),
        0,
        inverse=True,
    )

    assert reconstructed.amplitudes == pytest.approx(state.amplitudes, abs=1e-12)
    assert dual_round_trip_error(state, (4, 5)) < 1e-12


def test_twenty_state_search_uses_multiple_torus_stages() -> None:
    result = search_torus_register((4, 5), (7,), top_k=4)

    assert result.total_states == 20
    assert result.iterations == 3
    assert result.success_probability > 0.99
    assert result.dual_round_trip_error < 1e-12
    assert result.ranked_states[0].index == 7
    assert result.ranked_states[0].coordinates == (1, 2)
    assert len(result.stages) > 3
    assert result.stages[0].marked_probability == pytest.approx(1.0 / 20.0)
    assert result.stages[-1].marked_probability == pytest.approx(
        result.success_probability
    )
    assert result.model_status == "DER"
    assert result.verification_type == "software_test"
    assert result.claims_experimental_verification is False


def test_qudit_search_fails_closed_on_invalid_registers() -> None:
    with pytest.raises(ValueError, match="more than three states"):
        search_torus_register((3,), (1,))
    with pytest.raises(ValueError, match="unique"):
        search_torus_register((4,), (1, 1))
    with pytest.raises(ValueError, match="outside"):
        search_torus_register((4,), (4,))
