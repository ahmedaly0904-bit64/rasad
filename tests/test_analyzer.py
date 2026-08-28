import math

import numpy as np
import pytest

from rasad.analyzer import THRESHOLDS, classify, summarize


def test_constant_values_have_zero_spread():
    result = summarize([7.0] * 50)
    assert result["std"] == 0.0
    assert result["cv"] == 0.0
    assert result["mean"] == 7.0
    assert result["min"] == 7.0
    assert result["max"] == 7.0


def test_cv_is_infinite_when_mean_is_zero():
    result = summarize([-1.0, 1.0])
    assert result["mean"] == 0.0
    assert math.isinf(result["cv"])


def test_std_estimates_known_sigma():
    rng = np.random.default_rng(42)
    values = rng.normal(loc=10.0, scale=2.0, size=20000)
    result = summarize(values)
    assert abs(result["std"] - 2.0) < 0.05
    assert abs(result["mean"] - 10.0) < 0.05


def test_percentile_interval_covers_ninety_percent():
    values = list(range(101))
    result = summarize(values)
    assert result["p05"] == pytest.approx(5.0)
    assert result["p95"] == pytest.approx(95.0)


def test_reports_the_number_of_values():
    assert summarize([1.0, 2.0, 3.0])["n"] == 3


def test_requires_at_least_two_values():
    with pytest.raises(ValueError, match="at least 2"):
        summarize([1.0])


def test_classify_boundaries():
    assert classify(0.0) == "robust"
    assert classify(0.049) == "robust"
    assert classify(THRESHOLDS["robust"]) == "wobbly"
    assert classify(0.20) == "wobbly"
    assert classify(0.201) == "fragile"
    assert classify(math.inf) == "fragile"
