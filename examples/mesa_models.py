"""رَصَد على نماذج Mesa — إطار محاكاة خارجي لم يُكتب لأجل رَصَد.

يوضح هذا المثال أن الواجهة تعمل على محاكاة لم تُصمَّم لهذه الأداة: يكفي
غلافٌ يستقبل ``(params, seed)`` ويرجّع قاموسًا.

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
    """يبني دالة ``run`` مطابقة لواجهة رَصَد فوق أي نموذج Mesa.

    Parameters
    ----------
    model_cls
        صنف النموذج في Mesa.
    scenario_cls
        صنف السيناريو المقابل، يستقبل البذرة عبر ``rng``.
    reporters
        اسم المخرَج في التقرير، مقابل اسم العمود عند جامع البيانات.

    Returns
    -------
    Callable[[dict, int], dict]
        دالة تشغيل واحدة، ترجّع القيم النهائية ومسارًا زمنيًا.
    """

    def run(params: dict, seed: int) -> dict:
        model = model_cls(scenario_cls(rng=seed))
        for _ in range(STEPS):
            model.step()

        frame = model.datacollector.get_model_vars_dataframe()
        out = {name: frame[column].iloc[-1] for name, column in reporters.items()}
        # مصفوفة numpy عمدًا: هكذا تُخرج المحاكاة الحقيقية سلاسلها
        out["trace"] = frame[next(iter(reporters.values()))].to_numpy()
        return out

    return run


CASES = {
    "Schelling — الفصل السكني": make_run(
        Schelling, SchellingScenario, {"happy": "happy", "minority_pct": "minority_pct"}
    ),
    "WolfSheep — الافتراس": make_run(
        WolfSheep, WolfSheepScenario, {"wolves": "Wolves", "sheep": "Sheep"}
    ),
    "Boltzmann — توزيع الثروة": make_run(
        BoltzmannWealth, BoltzmannScenario, {"gini": "Gini"}
    ),
}


def main() -> None:
    for title, run in CASES.items():
        print(f"\n{'=' * 62}\n{title}\n{'=' * 62}")
        print(rasad.measure(run, params={}, runs=RUNS).summary())


if __name__ == "__main__":
    main()
