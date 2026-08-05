"""Unit tests for inside-out UPI Kernel engine and server HTTP endpoints."""

from __future__ import annotations

from upi.kernel import get_kernel


def test_upi_kernel_singleton_and_physics_execution() -> None:
    """Verify inside-out UPIKernel operates correctly."""
    kernel = get_kernel()
    status = kernel.generate_kernel_status()

    assert status["kernel_version"] == "0.1.0-alpha"
    assert status["status"] == "HEALTHY"
    assert status["claims_experimental_verification"] is False

    # Test physics frequency calculation
    freq_res = kernel.execute_physics_frequency(8.0)
    assert freq_res["status"] == "DER"
    assert freq_res["energy_j"] > 0.0
    assert freq_res["mass_equivalent_kg"] > 0.0

    # Test physics mass calculation
    mass_res = kernel.execute_physics_mass(1e-30)
    assert mass_res["status"] == "DER"
    assert mass_res["frequency_hz"] > 0.0

    # Test Qudit search via kernel
    qudit_res = kernel.search_qudit([4, 5], [7], iterations=2)
    assert qudit_res["status"] == "DER"
    assert qudit_res["total_states"] == 20
    assert 0.0 <= qudit_res["success_probability"] <= 1.0

    # Test DNA sonification via kernel
    dna_res = kernel.sonify_dna("ATGCGATACGA")
    assert dna_res["status"] == "DER"
    assert dna_res["total_bases"] == 11

    # Test SUNET network inspection via kernel
    sunet_res = kernel.inspect_sunet("KTH")
    assert sunet_res["status"] == "DER"
    assert len(sunet_res["matching_nodes"]) >= 2
