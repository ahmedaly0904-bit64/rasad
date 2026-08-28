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


def divergence(series: Sequence[Sequence[float]]) -> list[float]:
    """Measure how far apart a set of time series has drifted by time step.

    At each time step the runs are treated as a sample and the sample
    standard deviation is taken across runs; a flat zero curve means the
    runs agree, a growing curve means they are drifting apart.

    Parameters
    ----------
    series
        A sequence of equal-length time series, one per simulation run.

    Returns
    -------
    list[float]
        One sample standard deviation per time step, across runs.

    Raises
    ------
    ValueError
        When fewer than two series are provided, or when the series do
        not all have the same length.
    """
    rows = [np.asarray(row, dtype=float) for row in series]
    if len(rows) < 2:
        raise ValueError("need at least 2 series to measure divergence")
    if any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("all series must have the same length")

    stack = np.stack(rows)
    return [float(std) for std in stack.std(axis=0, ddof=1)]
