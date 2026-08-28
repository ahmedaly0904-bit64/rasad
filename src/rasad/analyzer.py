"""Arithmetic on sequences of numbers, nothing more.

This module knows nothing about simulations or how the numbers it is
given were produced. It only describes the spread and location of a
sample: count, mean, sample standard deviation, coefficient of
variation, extrema, and percentile interval.
"""

import math
from collections.abc import Sequence

import numpy as np

THRESHOLDS: dict[str, float] = {"robust": 0.05, "wobbly": 0.20}


def summarize(values: Sequence[float]) -> dict[str, float | int]:
    """Summarize a sample of numbers.

    Parameters
    ----------
    values
        A sequence of numeric values, e.g. repeated simulation runs.

    Returns
    -------
    dict
        Keys ``n``, ``mean``, ``std``, ``cv``, ``min``, ``max``, ``p05``, ``p95``.
        ``std`` is the sample standard deviation (``ddof=1``); ``cv`` is
        ``std / abs(mean)`` and is infinite when the mean is zero.

    Raises
    ------
    ValueError
        When fewer than two values are provided.
    """
    arr = np.asarray(values, dtype=float)
    if arr.size < 2:
        raise ValueError("need at least 2 values to summarize")

    n = int(arr.size)
    mean = float(arr.mean())
    std = float(arr.std(ddof=1))
    cv = math.inf if mean == 0.0 else std / abs(mean)
    p05 = float(np.percentile(arr, 5))
    p95 = float(np.percentile(arr, 95))

    return {
        "n": n,
        "mean": mean,
        "std": std,
        "cv": cv,
        "min": float(arr.min()),
        "max": float(arr.max()),
        "p05": p05,
        "p95": p95,
    }


def classify(cv: float) -> str:
    """Label a coefficient of variation by its robustness cutoff.

    Parameters
    ----------
    cv
        The coefficient of variation of a sample.

    Returns
    -------
    str
        ``"robust"`` below the robust threshold, ``"wobbly"`` up to and
        including the wobbly threshold, ``"fragile"`` beyond it.
    """
    if cv < THRESHOLDS["robust"]:
        return "robust"
    if cv <= THRESHOLDS["wobbly"]:
        return "wobbly"
    return "fragile"
