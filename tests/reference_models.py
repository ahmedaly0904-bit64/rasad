"""Reference models whose behaviour is known analytically.

Each one exists so a statistical claim can be checked against a known
answer instead of against whatever the code currently produces.
"""

import numpy as np


def constant_model(params: dict, seed: int) -> dict:
    """Always returns the same number. Expect: standard deviation exactly zero."""
    return {"value": 42.0}


def seed_echo_model(params: dict, seed: int) -> dict:
    """Returns the seed itself. Expect: every run differs, no repeats."""
    return {"value": float(seed)}


def normal_model(params: dict, seed: int) -> dict:
    """Draws from a normal distribution with a known sigma from params."""
    rng = np.random.default_rng(seed)
    return {"value": float(rng.normal(params["mu"], params["sigma"]))}


def flat_series_model(params: dict, seed: int) -> dict:
    """A constant series. Expect: the divergence curve is flat at zero."""
    return {"trace": [1.0, 2.0, 3.0, 4.0, 5.0]}


def random_walk_model(params: dict, seed: int) -> dict:
    """A random walk. Expect: divergence grows as the square root of time."""
    rng = np.random.default_rng(seed)
    steps = params["steps"]
    return {"trace": np.cumsum(rng.normal(0.0, 1.0, steps)).tolist()}
