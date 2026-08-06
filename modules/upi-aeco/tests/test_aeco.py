from upi_aeco.adapters import UPI_RNA
from upi_aeco.core import evaluate, evolution_cycle, generate_candidates, observe, select


def test_upi_rna_adapter() -> None:
    rna = UPI_RNA()

    # Query
    q_res = rna.query("Compute hydrogen mass-frequency relation")
    assert "mapped_nodes_count" in q_res
    assert "raw_prompt" in q_res

    # Debug
    dbg = rna.debug()
    assert "total_nodes" in dbg
    assert "status_counts" in dbg

    # Odin evaluation
    val = rna.evaluate_odin()
    assert val > 0

    # Physics query
    phys_str = rna.evaluate_physics("What is Middle C C4?")
    assert "261.63" in phys_str


def test_observer_builds_self_model() -> None:
    model = observe("v0.1.0-test")
    assert model["version_id"] == "v0.1.0-test"
    assert "status_counts" in model
    assert "junk_clusters" in model
    assert "weak_domains" in model


def test_evaluator_runs_benchmarks() -> None:
    score = evaluate("v0.1.0-initial")
    assert 0.0 <= score <= 1.0


def test_mutator_enforces_boundaries() -> None:
    model = observe()
    candidates = generate_candidates("v0.1.0", model)

    assert len(candidates) > 0
    for cand in candidates:
        assert cand.startswith("v0.1.0")


def test_selector_promotes_improvement() -> None:
    promoted = select(
        current_version="v0.1.0",
        best_candidate="v0.1.0-better",
        base_score=0.5,
        best_score=0.8,
        min_improvement=0.02,
    )
    assert promoted == "v0.1.0-better"

    no_promotion = select(
        current_version="v0.1.0",
        best_candidate="v0.1.0-slight",
        base_score=0.5,
        best_score=0.501,
        min_improvement=0.02,
    )
    assert no_promotion == "v0.1.0"


def test_evolution_cycle_full_loop() -> None:
    res = evolution_cycle("v0.1.0-initial")

    assert res["operation"] == "upi_aeco_evolution_cycle"
    assert "previous_version" in res
    assert "promoted_version" in res
    assert res["candidates_evaluated"] > 0
    assert 0.0 <= res["best_score"] <= 1.0
