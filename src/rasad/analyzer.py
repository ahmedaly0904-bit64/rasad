"""Arithmetic on sequences of numbers, nothing more.

This module knows nothing about simulations or how the numbers it is
given were produced. It only describes the spread and location of a
sample: count, mean, sample standard deviation, coefficient of
variation, extrema, and percentile interval.
"""

import math
from collections.abc import Sequence

import numpy as np

# Default classification cutoffs. These are a convention chosen by the
# project's authors, not a derived or theoretical result: a caller may
# pass their own thresholds to ``classify`` and ``rasad.measure``, in
# which case these defaults are ignored.
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
        ``std / abs(mean)``; it is zero whenever ``std`` is zero, and
        infinite when the mean is zero but the values still vary.

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
    # ترتيب الفحص مقصود: انحراف صفر يعني قيمة محددة تمامًا مهما كان المتوسط.
    # لولا هذا لصُنّف مخرَج ثابت عند صفر "هشًا" وهو أثبت ما يكون.
    if std == 0.0:
        cv = 0.0
    elif mean == 0.0:
        cv = math.inf
    else:
        cv = std / abs(mean)
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


def validate_thresholds(thresholds: dict[str, float]) -> dict[str, float]:
    """Check caller-supplied classification cutoffs and copy them.

    The thresholds are a convention, not a measured property of the data,
    so whatever the caller passes is taken as-is once it passes these
    checks.

    Parameters
    ----------
    thresholds
        A dict with exactly the keys ``robust`` and ``wobbly``. Both
        values must be finite numbers greater than 0, and ``robust``
        must be strictly below ``wobbly``.

    Returns
    -------
    dict[str, float]
        A plain-float copy of ``thresholds``, so mutating the caller's
        dict afterwards cannot change the classification.

    Raises
    ------
    ValueError
        When the keys, the positivity/finiteness, or the ordering of the
        values do not satisfy the rules above.
    """
    keys = set(thresholds)
    if keys != {"robust", "wobbly"}:
        raise ValueError(
            f"thresholds must have exactly the keys 'robust' and 'wobbly', got {sorted(keys)}"
        )
    robust = thresholds["robust"]
    wobbly = thresholds["wobbly"]
    for name, value in (("robust", robust), ("wobbly", wobbly)):
        if not (math.isfinite(value) and value > 0):
            raise ValueError(f"{name} threshold must be a finite positive number, got {value!r}")
    if not robust < wobbly:
        raise ValueError("robust must be below wobbly")
    return {"robust": float(robust), "wobbly": float(wobbly)}


def classify(cv: float, thresholds: dict[str, float] | None = None) -> str:
    """Label a coefficient of variation by its robustness cutoff.

    Parameters
    ----------
    cv
        The coefficient of variation of a sample.
    thresholds
        The classification cutoffs. ``None`` means use the module-level
        :data:`THRESHOLDS` default; any other dict is validated with
        :func:`validate_thresholds` first.

    Returns
    -------
    str
        ``"robust"`` below the robust threshold, ``"wobbly"`` up to and
        including the wobbly threshold, ``"fragile"`` beyond it.
    """
    # kept as if/else rather than a ternary: the two branches do different
    # things — one picks a default, the other validates untrusted input.
    if thresholds is None:  # noqa: SIM108
        thresholds = THRESHOLDS
    else:
        thresholds = validate_thresholds(thresholds)
    if cv < thresholds["robust"]:
        return "robust"
    if cv <= thresholds["wobbly"]:
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
