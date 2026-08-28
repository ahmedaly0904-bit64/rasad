import pytest

from rasad.adapter import split_outputs, validate_model
from reference_models import constant_model, random_walk_model


def test_accepts_a_conforming_model():
    validate_model(constant_model)
    validate_model(random_walk_model)


def test_rejects_a_non_callable():
    with pytest.raises(TypeError, match="callable"):
        validate_model("not a function")


def test_rejects_wrong_parameter_names():
    def bad(config, rng_seed):
        return {}

    with pytest.raises(TypeError, match="params.*seed"):
        validate_model(bad)


def test_rejects_wrong_parameter_count():
    def bad(params):
        return {}

    with pytest.raises(TypeError, match="params.*seed"):
        validate_model(bad)


def test_splits_scalars_from_series():
    scalars, series = split_outputs({"pop": 500.0, "trace": [1.0, 2.0], "wars": 3})
    assert scalars == {"pop": 500.0, "wars": 3.0}
    assert series == {"trace": [1.0, 2.0]}


def test_scalars_are_plain_floats():
    scalars, _ = split_outputs({"wars": 3})
    assert type(scalars["wars"]) is float


def test_rejects_a_boolean_output():
    with pytest.raises(TypeError, match="unsupported output"):
        split_outputs({"collapsed": True})


def test_rejects_a_string_output():
    with pytest.raises(TypeError, match="unsupported output"):
        split_outputs({"name": "Nation_A"})
