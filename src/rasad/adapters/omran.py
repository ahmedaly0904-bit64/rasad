"""Wrap Omran from the outside so Rasad can measure it.

This file lives in the Rasad repository. It imports Omran's ``nation`` and
``world`` modules by putting Omran's ``src`` directory on ``sys.path`` at
call time, and drives Omran purely through its public interface. Nothing
inside the Omran project is created, modified, or deleted.
"""

import contextlib
import io
import random
import sys
from collections.abc import Callable


def make_omran_run(omran_src: str, years: int) -> Callable[[dict, int], dict]:
    """Build a Rasad-compatible model function that runs Omran.

    Parameters
    ----------
    omran_src
        Absolute path to Omran's ``src`` directory. It is inserted at the
        front of ``sys.path`` if not already present, so that ``nation``
        and ``world`` can be imported from outside the Omran project.
    years
        How many simulated years each run performs.

    Returns
    -------
    Callable[[dict, int], dict]
        A closure ``run(params, seed)`` that seeds Python's global RNG,
        builds a fresh set of nations, steps Omran's ``WorldModel`` for
        ``years`` years with stdout suppressed, and returns Omran's output
        as scalars plus a population trace.
    """
    if omran_src not in sys.path:
        sys.path.insert(0, omran_src)

    from nation import Nation
    from world import WorldModel

    def run(params: dict, seed: int) -> dict:
        random.seed(seed)

        nations = [
            Nation(name="Nation_A", population=500, food=2000, growth_rate=0.03),
            Nation(name="Nation_B", population=80, food=2000, growth_rate=0.035),
            Nation(name="Nation_C", population=200, food=2000, growth_rate=0.032),
        ]

        population_trace = []
        with contextlib.redirect_stdout(io.StringIO()):
            world = WorldModel(nations)
            for _ in range(years):
                world.step()
                population_trace.append(
                    sum(n.population for n in world.nations if n.is_alive)
                )

        return {
            "final_total_population": float(
                sum(n.population for n in world.nations if n.is_alive)
            ),
            "survivors": float(sum(1 for n in world.nations if n.is_alive)),
            "total_wars": float(sum(n.war_count for n in world.nations)),
            "total_famines": float(sum(n.famine_count for n in world.nations)),
            "population_trace": [float(value) for value in population_trace],
        }

    return run
