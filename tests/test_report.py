import pytest
from reference_models import (
    constant_model,
    empty_series_model,
    flat_series_model,
    nan_series_model,
    normal_model,
    random_walk_model,
    shape_drift_model,
    tiny_value_model,
)

import rasad
from rasad.report import _fmt


def test_constant_model_has_low_variability():
    report = rasad.measure(constant_model, params={}, runs=20)
    assert report.scalars["value"]["std"] == 0.0
    assert report.scalars["value"]["variability"] == "low"


def test_wide_normal_model_has_high_variability():
    report = rasad.measure(normal_model, params={"mu": 1.0, "sigma": 5.0}, runs=200)
    assert report.scalars["value"]["variability"] == "high"


def test_narrow_normal_model_has_low_variability():
    report = rasad.measure(normal_model, params={"mu": 100.0, "sigma": 0.01}, runs=200)
    assert report.scalars["value"]["variability"] == "low"


def test_flat_series_never_diverges():
    report = rasad.measure(flat_series_model, params={}, runs=10)
    assert report.series["trace"] == [0.0, 0.0, 0.0, 0.0, 0.0]


def test_random_walk_diverges_over_time():
    report = rasad.measure(random_walk_model, params={"steps": 50}, runs=300)
    spread = report.series["trace"]
    assert spread[0] < spread[25] < spread[49]


def test_report_records_the_run_count():
    assert rasad.measure(constant_model, params={}, runs=12).runs == 12


def test_same_seeds_produce_an_identical_report():
    a = rasad.measure(normal_model, params={"mu": 1.0, "sigma": 1.0}, runs=30)
    b = rasad.measure(normal_model, params={"mu": 1.0, "sigma": 1.0}, runs=30)
    assert a.scalars == b.scalars
    assert a.series == b.series
    assert a.summary() == b.summary()


def test_a_different_base_seed_changes_the_result():
    a = rasad.measure(normal_model, params={"mu": 1.0, "sigma": 1.0}, runs=30)
    b = rasad.measure(normal_model, params={"mu": 1.0, "sigma": 1.0}, runs=30, base_seed=999)
    assert a.scalars != b.scalars


def test_summary_names_every_output_and_its_variability():
    text = rasad.measure(constant_model, params={}, runs=20).summary()
    assert "value" in text
    assert "low" in text
    assert "20" in text


def test_measure_rejects_fewer_than_two_runs():
    with pytest.raises(ValueError, match="at least 2"):
        rasad.measure(constant_model, params={}, runs=1)


def test_measure_rejects_an_output_that_changes_shape_between_runs():
    with pytest.raises(ValueError, match="output 'v'"):
        rasad.measure(shape_drift_model, params={}, runs=100)


def test_measure_rejects_a_series_that_is_always_empty():
    with pytest.raises(ValueError, match="at least one time step"):
        rasad.measure(empty_series_model, params={}, runs=5)


def test_measure_rejects_a_series_containing_a_nan():
    with pytest.raises(ValueError, match="non-finite values"):
        rasad.measure(nan_series_model, params={}, runs=5)


def test_plot_has_one_trace_per_series():
    report = rasad.measure(random_walk_model, params={"steps": 20}, runs=50)
    fig = report.plot()
    assert len(fig.data) == 1
    assert fig.data[0].name == "trace"


def test_plot_y_values_match_the_divergence_numbers():
    report = rasad.measure(random_walk_model, params={"steps": 20}, runs=50)
    fig = report.plot()
    assert list(fig.data[0].y) == report.series["trace"]
    assert list(fig.data[0].x) == list(range(20))


def test_plot_raises_when_there_are_no_series():
    report = rasad.measure(constant_model, params={}, runs=10)
    with pytest.raises(ValueError, match="no time series"):
        report.plot()


def test_custom_thresholds_change_the_variability():
    lenient = rasad.measure(
        normal_model, params={"mu": 100.0, "sigma": 3.0}, runs=200
    )
    strict = rasad.measure(
        normal_model,
        params={"mu": 100.0, "sigma": 3.0},
        runs=200,
        thresholds={"low": 0.001, "moderate": 0.005},
    )
    assert lenient.scalars["value"]["variability"] == "low"
    assert strict.scalars["value"]["variability"] == "high"


def test_report_records_the_thresholds_it_used():
    report = rasad.measure(constant_model, params={}, runs=10)
    assert report.thresholds == {"low": 0.05, "moderate": 0.20}


def test_summary_states_the_thresholds_and_calls_them_a_convention():
    text = rasad.measure(constant_model, params={}, runs=10).summary()
    assert "convention" in text
    assert "0.0500" in text or "0.05" in text


def test_bad_thresholds_fail_before_any_run():
    calls = []

    def counting_model(params, seed):
        calls.append(seed)
        return {"value": 1.0}

    with pytest.raises(ValueError):
        rasad.measure(
            counting_model, params={}, runs=50, thresholds={"low": 0.9, "moderate": 0.1}
        )
    assert calls == []


def test_fmt_keeps_small_magnitudes_visible():
    assert _fmt(0.0) == "0.00"
    assert _fmt(1234.5) == "1,234.50"
    assert _fmt(0.01) == "0.01"
    assert _fmt(0.005) == "0.01"
    assert _fmt(0.001) == "0.001"
    assert _fmt(-0.001) == "-0.001"
    assert _fmt(1.2e-9) == "1.2e-09"
    assert _fmt(float("inf")) == "inf"


def test_summary_does_not_render_a_small_output_as_zero():
    text = rasad.measure(tiny_value_model, params={}, runs=20).summary()
    line = next(row for row in text.splitlines() if row.strip().startswith("value:"))
    assert "mean 0.00 " not in line
    assert "0.001" in line
