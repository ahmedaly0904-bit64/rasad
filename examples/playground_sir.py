"""A sandbox — Rasad on an SIR epidemic simulation.

Run it as is first, then change it.
Each section is independent — you can comment out what you don't want.
"""

import EoN
import networkx as nx
import numpy as np

import rasad

# ═════════════════════════════════════════════════════════
# The community — 500 people, a relationship network fixed in every run
# ═════════════════════════════════════════════════════════
G = nx.barabasi_albert_graph(500, 3, seed=1)


# ═════════════════════════════════════════════════════════
# 1 — one epidemic in your hands
# ═════════════════════════════════════════════════════════
print("=" * 55)
print("1 — one epidemic, seed 1")
print("=" * 55)

t, S, I, R = EoN.fast_SIR(G, tau=0.3, gamma=1.0, rho=0.02,
                          rng=np.random.default_rng(1))

print(f"  peak infected:       {I.max()}")
print(f"  infected in the end: {R[-1]} of {G.number_of_nodes()}")
print(f"  epidemic duration:   {t[-1]:.2f}")


# ═════════════════════════════════════════════════════════
# 2 — everything the same, a different seed
# ═════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("2 — the same disease and community, different seeds")
print("=" * 55)

for seed in (1, 2, 3, 4, 5):
    t, S, I, R = EoN.fast_SIR(G, tau=0.3, gamma=1.0, rho=0.02,
                              rng=np.random.default_rng(seed))
    print(f"  seed {seed}:  peak {I.max():3d}  |  infected {R[-1]:3d}  |  duration {t[-1]:5.2f}")

print("\n  ← is one of them the truth? none. that's why Rasad exists.")


# ═════════════════════════════════════════════════════════
# 3 — wrap the simulation in a function in the shape Rasad understands
# ═════════════════════════════════════════════════════════
def run(params, seed):
    """One run. The seed comes from outside, and we return a dict of numbers."""
    t, S, I, R = EoN.fast_SIR(
        G,
        tau=params["tau"],
        gamma=params["gamma"],
        rho=0.02,
        rng=np.random.default_rng(seed),
    )
    return {
        "peak": I.max(),
        "total_infected": R[-1],
        "duration": t[-1],
    }


# ═════════════════════════════════════════════════════════
# 4 — run Rasad
# ═════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("4 — Rasad: 50 epidemics, a strong disease (tau=0.3)")
print("=" * 55)

report = rasad.measure(run, params={"tau": 0.3, "gamma": 1.0}, runs=50)
print(report.summary())


# ═════════════════════════════════════════════════════════
# 5 — the same thing with a weaker disease
#     predict the difference before you run it
# ═════════════════════════════════════════════════════════
print("\n" + "=" * 55)
print("5 — a weaker disease (tau=0.12)")
print("=" * 55)

report_weak = rasad.measure(run, params={"tau": 0.12, "gamma": 1.0}, runs=50)
print(report_weak.summary())


# ═════════════════════════════════════════════════════════
# ✍️  Try it yourself:
#
#   • Change tau or gamma above
#   • Add a new output in return — for example "never_infected": S[-1]
#   • Change runs from 50 to 200 and see whether the variability labels hold
#   • Change the community size in barabasi_albert_graph
# ═════════════════════════════════════════════════════════
