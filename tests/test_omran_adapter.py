import os

import pytest

from rasad.adapter import split_outputs, validate_model
from rasad.adapters.omran import make_omran_run

OMRAN_SRC = os.environ.get("OMRAN_SRC", "../civilization_sim/src")

pytestmark = pytest.mark.skipif(
    not os.path.isdir(OMRAN_SRC), reason="Omran source not available"
)


def test_run_conforms_to_the_model_interface():
    validate_model(make_omran_run(OMRAN_SRC, years=10))


def test_output_types_are_all_supported():
    run = make_omran_run(OMRAN_SRC, years=10)
    scalars, series = split_outputs(run({}, 1))
    assert set(scalars) == {
        "final_total_population",
        "survivors",
        "total_wars",
        "total_famines",
    }
    assert set(series) == {"population_trace"}


def test_trace_length_matches_the_requested_years():
    run = make_omran_run(OMRAN_SRC, years=7)
    assert len(run({}, 1)["population_trace"]) == 7


def test_runs_are_quiet():
    """Omran prints on construction; the adapter must swallow it."""
    import contextlib
    import io

    run = make_omran_run(OMRAN_SRC, years=5)
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        run({}, 1)
    assert buffer.getvalue() == ""


def test_unknown_params_are_rejected_instead_of_ignored():
    run = make_omran_run(OMRAN_SRC, years=5)
    with pytest.raises(ValueError, match="growth_rate"):
        run({"growth_rate": 0.05}, 1)


def test_default_nations_are_used_when_params_is_empty():
    run = make_omran_run(OMRAN_SRC, years=5)
    out = run({}, 1)
    assert out["survivors"] <= 3
    assert set(out) == {
        "final_total_population",
        "survivors",
        "total_wars",
        "total_famines",
        "population_trace",
    }


def test_nations_can_be_configured_through_params():
    run = make_omran_run(OMRAN_SRC, years=5)
    out = run(
        {
            "nations": [
                {"name": "A", "population": 100, "food": 500, "growth_rate": 0.03},
                {"name": "B", "population": 100, "food": 500, "growth_rate": 0.03},
            ]
        },
        1,
    )
    assert out["survivors"] <= 2
    assert len(out["population_trace"]) == 5
