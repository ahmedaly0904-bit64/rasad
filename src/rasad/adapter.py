"""Check that a user model fits the required interface and sort its output.

A model is any plain function matching the required simulation
interface::

    def run(params: dict, seed: int) -> dict: ...

This module validates that a candidate function actually has those two
parameters, and splits a returned result dict into scalar results (a
single final number) and time series (lists of numbers), rejecting
anything a simulation should never produce.
"""

import inspect
from collections.abc import Callable
from typing import Any


def validate_model(fn: Callable[..., dict]) -> None:
    """Check that a function matches the required model interface.

    Parameters
    ----------
    fn
        The candidate model, expected to accept exactly ``params`` and
        ``seed`` as its first two parameters.

    Raises
    ------
    TypeError
        When ``fn`` is not callable, or when its first two parameter
        names are not exactly ``("params", "seed")``.
    """
    if not callable(fn):
        raise TypeError(f"model must be callable, got {type(fn).__name__}")

    names = [p.name for p in inspect.signature(fn).parameters.values()][:2]
    if names != ["params", "seed"]:
        raise TypeError(
            f"model must accept (params, seed) as its first two arguments, got ({', '.join(names)})"
        )


def split_outputs(out: dict[str, Any]) -> tuple[dict[str, float], dict[str, list[float]]]:
    """Split a model result into scalar results and time series.

    Parameters
    ----------
    out
        The dict returned by a model run. Each value must be a number
        (a scalar result) or a list/tuple of numbers (a time series).

    Returns
    -------
    tuple[dict[str, float], dict[str, list[float]]]
        ``(scalars, series)``: scalars holds each single-number output
        as a plain ``float``, series holds each sequence output as a
        ``list[float]``.

    Raises
    ------
    TypeError
        When a value is a ``bool``, a ``str``, ``bytes``, or any other
        type that is neither a single number nor a sequence of numbers.
    """
    scalars: dict[str, float] = {}
    series: dict[str, list[float]] = {}

    for key, value in out.items():
        if isinstance(value, bool):
            raise TypeError(f"unsupported output {key!r}: boolean values are not allowed")
        if isinstance(value, (int, float)):
            scalars[key] = float(value)
        elif isinstance(value, (list, tuple)):
            series[key] = [float(item) for item in value]
        else:
            raise TypeError(
                f"unsupported output {key!r}: must be a number or a sequence of numbers"
            )

    return scalars, series
