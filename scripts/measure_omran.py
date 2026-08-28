"""Measure how robust Omran's results are — 100 runs, 100 simulated years."""

import rasad
from rasad.adapters.omran import make_omran_run

OMRAN_SRC = "$OMRAN_SRC"

run = make_omran_run(OMRAN_SRC, years=100)
report = rasad.measure(run, params={}, runs=100)

print(report.summary())
report.plot().write_html("omran_divergence.html")
print("\nChart written to omran_divergence.html")
