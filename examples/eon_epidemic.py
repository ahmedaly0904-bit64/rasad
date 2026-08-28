"""رَصَد على EoN — انتشار وباء على شبكة.

الهيكل جاهز. المطلوب منك: تقرر تقيس إيه، وتحل مشكلة اختلاف أطوال السلاسل.

    .venv/bin/python examples/eon_epidemic.py
"""

import EoN
import networkx as nx
import numpy as np

import rasad

# ——— معاملات المحاكاة ———
NODES = 500        # عدد الأفراد في الشبكة
TAU = 0.3          # معدل العدوى
GAMMA = 1.0        # معدل الشفاء
RHO = 0.02         # نسبة المصابين في البداية

# الشبكة ثابتة عبر كل التشغيلات — البذرة تغيّر مسار الوباء لا بنية المجتمع
GRAPH = nx.barabasi_albert_graph(NODES, 3, seed=1)


def run(params: dict, seed: int) -> dict:
    """تشغيلة واحدة لوباء على الشبكة.

    t, S, I, R كلها مصفوفات numpy بنفس الطول — لكن الطول **يختلف بين
    التشغيلات**، لأن كل حدث عدوى أو شفاء يسجّل صفًا.
    """
    t, S, I, R = EoN.fast_SIR(
        GRAPH,
        tau=params.get("tau", TAU),
        gamma=params.get("gamma", GAMMA),
        rho=params.get("rho", RHO),
        rng=np.random.default_rng(seed),
    )

    # على شبكة زمنية ثابتة: كل التشغيلات تُقاس عند نفس اللحظات،
    # فتصبح المقارنة بينها ذات معنى. بدون هذا تختلف الأطوال ويرفض رَصَد.
    grid = np.linspace(0.0, 15.0, 60)
    infected_on_grid = np.interp(grid, t, I)

    return {
        "peak_infected": I.max(),
        "final_infected_total": R[-1],
        "never_infected": S[-1],
        "epidemic_duration": t[-1],
        "took_off": 1.0 if R[-1] > 0.1 * NODES else 0.0,
        "infected_curve": infected_on_grid,
    }


def main() -> None:
    report = rasad.measure(run, params={}, runs=50)
    print(report.summary())

    if report.series:
        report.plot().write_html("eon_divergence.html")
        print("\nالرسم: eon_divergence.html")


if __name__ == "__main__":
    main()
