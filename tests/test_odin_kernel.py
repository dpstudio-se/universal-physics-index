
from upi.odin_kernel import EthicSingularity, OdinCoreKernel, OdinCoreState


def test_ethic_singularity_entropy_check() -> None:
    singularity = EthicSingularity()

    assert singularity.entropy == 0.0
    assert singularity.collapsed is False

    # Normal text reduces or maintains zero entropy
    singularity.check("Normal text")
    assert singularity.entropy == 0.0

    # Review keyword increases entropy
    singularity.check("Anpassa detta sammanhang")
    assert singularity.entropy == 10.0
    assert len(singularity.audit_logs) == 1


def test_odin_core_state_8hz_pulse() -> None:
    state = OdinCoreState()
    assert state.cycle_ms == 125.0

    factor = state.pulse(125.0)
    assert factor > 0.0
    assert state.torus == 1.0


def test_selfish_gene_loop_tf1776_scan() -> None:
    kernel = OdinCoreKernel()

    report = kernel.run_selfish_gene_loop("Censur är förbjuden enligt TF1776", iterations=184)
    assert report.iterations_run == 184
    assert report.censorship_detected is True
    assert report.transparency_score < 1.0


def test_evaluate_odin_formula() -> None:
    kernel = OdinCoreKernel()

    res = kernel.evaluate_odin_formula(8.0)
    assert res["frequency_hz"] == 8.0
    assert res["mass_equivalent_kg"] > 0
    assert res["v_odin_magnitude"] > 0
    assert res["status"] == "DER"


def test_generate_status_report() -> None:
    kernel = OdinCoreKernel()
    report = kernel.generate_status_report()

    assert "odin_core_status" in report
    assert report["odin_core_status"]["tripp"] == 1.0
    assert report["dna_identity"]["dna_login"] == "Ω^8200"
    assert report["high_law"] == "TF1776 - INFORMATION IS FREE"
