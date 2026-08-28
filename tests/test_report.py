import pytest

import rasad
from reference_models import (
    constant_model,
    flat_series_model,
    normal_model,
    random_walk_model,
)


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
