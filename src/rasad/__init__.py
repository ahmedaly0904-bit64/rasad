"""رَصَد — measuring the robustness of simulation results."""

from collections.abc import Callable
from typing import Any

from rasad.adapter import split_outputs
from rasad.analyzer import classify, divergence, summarize
from rasad.report import Report
from rasad.runner import run_all
from rasad.sampler import make_plan

__all__ = ["measure", "Report"]


def measure(
    fn: Callable[..., dict],
    params: dict[str, Any],
    runs: int = 100,
    base_seed: int = 0,
) -> Report:
    """Measure the robustness of a simulation model's output.

    Parameters
    ----------
    fn
        A model matching the simulation interface
        ``def run(params: dict, seed: int) -> dict``.
    params
        The simulation parameters, fixed across every run.
    runs
        How many runs to make. Must be at least 2.
    base_seed
        The seed of the first run; run ``i`` gets ``base_seed + i``.

    Returns
    -------
    Report
        Per scalar output its summary plus a verdict, per series output
        its divergence curve, and the run count.

    Raises
    ------
    ValueError
        When ``runs`` is below 2.
    """
    plan = make_plan(params, runs, base_seed)
    results = run_all(fn, plan)

    scalar_values: dict[str, list[float]] = {}
    series_curves: dict[str, list[list[float]]] = {}
    for out in results:
        scalars, series = split_outputs(out)
        for name, value in scalars.items():
            scalar_values.setdefault(name, []).append(value)
        for name, curve in series.items():
            series_curves.setdefault(name, []).append(curve)

    scalars: dict[str, dict[str, Any]] = {}
    for name, values in scalar_values.items():
        stats = summarize(values)
        stats["verdict"] = classify(stats["cv"])
        scalars[name] = stats

    series = {name: divergence(curves) for name, curves in series_curves.items()}

    return Report(scalars=scalars, series=series, runs=runs)
