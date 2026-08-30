import pytest
from reference_models import (
    constant_model,
    flat_series_model,
    normal_model,
    random_walk_model,
)

import rasad


def test_constant_model_is_robust():
    report = rasad.measure(constant_model, params={}, runs=20)
    assert report.scalars["value"]["std"] == 0.0
    assert report.scalars["value"]["verdict"] == "robust"


def test_wide_normal_model_is_fragile():
    report = rasad.measure(normal_model, params={"mu": 1.0, "sigma": 5.0}, runs=200)
    assert report.scalars["value"]["verdict"] == "fragile"


def test_narrow_normal_model_is_robust():
    report = rasad.measure(normal_model, params={"mu": 100.0, "sigma": 0.01}, runs=200)
    assert report.scalars["value"]["verdict"] == "robust"


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


def test_summary_names_every_output_and_its_verdict():
    text = rasad.measure(constant_model, params={}, runs=20).summary()
    assert "value" in text
    assert "صامد" in text
    assert "20" in text


def test_measure_rejects_fewer_than_two_runs():
    with pytest.raises(ValueError, match="at least 2"):
        rasad.measure(constant_model, params={}, runs=1)


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


def test_custom_thresholds_change_the_verdict():
    lenient = rasad.measure(
        normal_model, params={"mu": 100.0, "sigma": 3.0}, runs=200
    )
    strict = rasad.measure(
        normal_model,
        params={"mu": 100.0, "sigma": 3.0},
        runs=200,
        thresholds={"robust": 0.001, "wobbly": 0.005},
    )
    assert lenient.scalars["value"]["verdict"] == "robust"
    assert strict.scalars["value"]["verdict"] == "fragile"


def test_report_records_the_thresholds_it_used():
    report = rasad.measure(constant_model, params={}, runs=10)
    assert report.thresholds == {"robust": 0.05, "wobbly": 0.20}


def test_summary_states_the_thresholds_and_calls_them_a_convention():
    text = rasad.measure(constant_model, params={}, runs=10).summary()
    assert "اصطلاح" in text
    assert "0.0500" in text or "0.05" in text


def test_bad_thresholds_fail_before_any_run():
    calls = []

    def counting_model(params, seed):
        calls.append(seed)
        return {"value": 1.0}

    with pytest.raises(ValueError):
        rasad.measure(
            counting_model, params={}, runs=50, thresholds={"robust": 0.9, "wobbly": 0.1}
        )
    assert calls == []
