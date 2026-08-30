"""Rasad on Mesa models — an external simulation framework not written for Rasad.

This example shows that the interface works on a simulation that was not
designed for this tool: a wrapper that accepts ``(params, seed)`` and
returns a dict is enough.

    pip install -e ".[examples]"
    python examples/mesa_models.py
"""

from mesa.examples import BoltzmannWealth, Schelling, WolfSheep
from mesa.examples.advanced.wolf_sheep.model import WolfSheepScenario
from mesa.examples.basic.boltzmann_wealth_model.model import BoltzmannScenario
from mesa.examples.basic.schelling.model import SchellingScenario

import rasad

STEPS = 40
RUNS = 25


def make_run(model_cls, scenario_cls, reporters: dict[str, str]):
    """Build a ``run`` function matching the Rasad interface on top of any Mesa model.

    Parameters
    ----------
    model_cls
        The model class in Mesa.
    scenario_cls
        The matching scenario class, which receives the seed via ``rng``.
    reporters
        The output name in the report, mapped to the column name in the
        data collector.

    Returns
    -------
    Callable[[dict, int], dict]
        A single run function, returning the final values and a time series.
    """

    def run(params: dict, seed: int) -> dict:
        model = model_cls(scenario_cls(rng=seed))
        for _ in range(STEPS):
            model.step()

        frame = model.datacollector.get_model_vars_dataframe()
        out = {name: frame[column].iloc[-1] for name, column in reporters.items()}
        # A numpy array on purpose: that is how a real simulation returns its series
        out["trace"] = frame[next(iter(reporters.values()))].to_numpy()
        return out

    return run


CASES = {
    "Schelling — residential segregation": make_run(
        Schelling, SchellingScenario, {"happy": "happy", "minority_pct": "minority_pct"}
    ),
    "WolfSheep — predation": make_run(
        WolfSheep, WolfSheepScenario, {"wolves": "Wolves", "sheep": "Sheep"}
    ),
    "Boltzmann — wealth distribution": make_run(
        BoltzmannWealth, BoltzmannScenario, {"gini": "Gini"}
    ),
}


def main() -> None:
    for title, run in CASES.items():
        print(f"\n{'=' * 62}\n{title}\n{'=' * 62}")
        print(rasad.measure(run, params={}, runs=RUNS).summary())


if __name__ == "__main__":
    main()
