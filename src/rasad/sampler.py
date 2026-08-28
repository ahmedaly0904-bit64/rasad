"""Decide what the simulation runs will be.

In this version the parameters stay fixed across every run and only the
random seed varies, so the measurement isolates one question: how much
of the result is pure randomness? Each plan entry is a fresh deep copy
of the parameters paired with a seed, so later runs can never disturb
earlier ones or the caller's original dict.
"""

import copy
from typing import Any


def make_plan(params: dict, runs: int, base_seed: int = 0) -> list[tuple[dict, int]]:
    """Build the list of (params, seed) pairs for a batch of runs.

    Parameters
    ----------
    params
        The simulation parameters. The same value is used for every
        run, and each run gets its own deep copy so mutations never
        leak between runs.
    runs
        How many runs to plan. Must be at least 2 so the results can
        be summarized.
    base_seed
        The seed of the first run; run ``i`` gets ``base_seed + i``.

    Returns
    -------
    list[tuple[dict, int]]
        One ``(params, seed)`` pair per run, in run order.

    Raises
    ------
    ValueError
        When ``runs`` is below 2.
    """
    if runs < 2:
        raise ValueError(f"need at least 2 runs to summarize, got {runs}")

    return [(copy.deepcopy(params), base_seed + i) for i in range(runs)]
