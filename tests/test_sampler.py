import pytest

from rasad.sampler import make_plan


def test_plan_has_one_entry_per_run():
    plan = make_plan({"a": 1}, runs=5)
    assert len(plan) == 5


def test_seeds_are_distinct_and_deterministic():
    plan = make_plan({}, runs=4, base_seed=100)
    assert [seed for _, seed in plan] == [100, 101, 102, 103]


def test_base_seed_defaults_to_zero():
    plan = make_plan({}, runs=3)
    assert [seed for _, seed in plan] == [0, 1, 2]


def test_same_inputs_produce_identical_plans():
    assert make_plan({"a": 1}, runs=3, base_seed=7) == make_plan(
        {"a": 1}, runs=3, base_seed=7
    )


def test_params_are_copied_not_shared():
    original = {"a": 1, "nested": {"b": 2}}
    plan = make_plan(original, runs=2)
    plan[0][0]["a"] = 999
    plan[0][0]["nested"]["b"] = 999
    assert plan[1][0]["a"] == 1
    assert plan[1][0]["nested"]["b"] == 2
    assert original["a"] == 1
    assert original["nested"]["b"] == 2


def test_rejects_fewer_than_two_runs():
    with pytest.raises(ValueError, match="at least 2"):
        make_plan({}, runs=1)
