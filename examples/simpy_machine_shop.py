"""رَصَد على SimPy — محاكاة أحداث متقطعة، معمارٌ مختلف تمامًا عن Mesa.

ورشة آلات: كل آلة تنتج قطعًا، وتتعطل في أوقات عشوائية، وتنتظر دورها عند
عامل صيانة واحد. سؤال الصلابة: كم قطعة تنتج الورشة، وهل الرقم خاصية في
النظام أم في البذرة؟

المثال مبني على نموذج «ورشة الآلات» المعروف في توثيق SimPy.

    pip install -e ".[examples]"
    python examples/simpy_machine_shop.py
"""

import random

import numpy as np
import simpy

import rasad

PT_MEAN, PT_SIGMA = 10.0, 2.0   # زمن إنتاج القطعة الواحدة
MTTF = 300.0                    # متوسط الزمن حتى العطل
REPAIR_TIME = 30.0              # زمن الإصلاح
WEEKS = 4
SIM_TIME = WEEKS * 7 * 24 * 60  # بالدقائق


class Machine:
    """آلة تنتج قطعًا وتتعطل ثم تُصلَح."""

    def __init__(self, env, rng, repairman):
        self.env = env
        self.rng = rng
        self.parts_made = 0
        self.broken = False
        self.process = env.process(self.working(repairman))
        env.process(self.break_machine())

    def working(self, repairman):
        while True:
            done_in = max(1.0, self.rng.normalvariate(PT_MEAN, PT_SIGMA))
            while done_in:
                try:
                    start = self.env.now
                    yield self.env.timeout(done_in)
                    done_in = 0
                except simpy.Interrupt:
                    self.broken = True
                    done_in -= self.env.now - start
                    with repairman.request(priority=1) as req:
                        yield req
                        yield self.env.timeout(REPAIR_TIME)
                    self.broken = False
            self.parts_made += 1

    def break_machine(self):
        while True:
            yield self.env.timeout(self.rng.expovariate(1.0 / MTTF))
            if not self.broken:
                self.process.interrupt()


def run(params: dict, seed: int) -> dict:
    """تشغيلة واحدة للورشة — واجهة رَصَد."""
    rng = random.Random(seed)
    env = simpy.Environment()
    repairman = simpy.PreemptiveResource(env, capacity=1)
    machines = [Machine(env, rng, repairman) for _ in range(params.get("machines", 10))]

    weekly_output = []
    for week in range(1, WEEKS + 1):
        env.run(until=week * 7 * 24 * 60)
        weekly_output.append(sum(m.parts_made for m in machines))

    total = sum(m.parts_made for m in machines)
    per_machine = [m.parts_made for m in machines]

    return {
        "total_parts": total,
        "best_machine": max(per_machine),
        "worst_machine": min(per_machine),
        "spread_between_machines": max(per_machine) - min(per_machine),
        "cumulative_output": np.array(weekly_output, dtype=float),
    }


def main() -> None:
    report = rasad.measure(run, params={"machines": 10}, runs=40)
    print(report.summary())


if __name__ == "__main__":
    main()
