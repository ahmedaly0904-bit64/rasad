# Rasad · رَصَد

**Measure how much of your simulation's result is a property of the model, and how much is the random seed.**

Stochastic simulations are usually reported without error bars. A paper says *"the civilisation
collapsed in year 240"* and never answers two questions:

1. If the random seed changes, is it still year 240?
2. Is this a property of the model, or an accident of one run?

Rasad answers both by measurement.

---

## Install

```bash
pip install -e .
```

Python 3.12+ · numpy · plotly

## Use

Describe your simulation as one function:

```python
def run(params: dict, seed: int) -> dict:
    """One run. A number is a final result; a list of numbers is a time series."""
    ...
```

Then:

```python
import rasad

report = rasad.measure(run, params={"growth": 0.03}, runs=100)
print(report.summary())
report.plot().write_html("divergence.html")
```

You get, for every output: mean, standard deviation, a 90% interval, and a verdict —
**robust**, **wobbly**, or **fragile** — plus a curve showing how far the runs drift
apart over time.

---

## What it found in practice

### A simulation that could not reproduce itself

Applied to [Omran](https://github.com/ahmedaly0904-bit64/Omran), an agent-based model of
Ibn Khaldun's theory of *asabiyyah*, **without modifying a line of it**:

```
final_total_population: mean 4,649.39 | cv 0.2841 | p05-p95 [2,704.75, 6,774.30] | fragile
survivors:              mean 1.14     | cv 0.3059 | p05-p95 [1.00, 2.00]        | fragile
total_wars:             mean 13.44    | cv 0.3986 | p05-p95 [6.00, 22.10]       | fragile
total_famines:          mean 0.00     | cv 0.0000 | p05-p95 [0.00, 0.00]        | robust
```

Nothing numeric in the model was robust. Worse, the measurement exposed something the author
did not know: **the same seed produced different results in different processes.**

Six runs with seed `1`, thirty simulated years:

```
1428 · 1428 · 1512 · 1426 · 1426 · 1512
```

Comparing the population curve year by year located the split: the runs are **identical for
nineteen years**, then diverge at year twenty by **one individual** — which becomes hundreds
by year one hundred. That is error propagation, measured.

Full write-up: [`FINDINGS.md`](FINDINGS.md)

### Aggregates can be stable while their parts are noise

On a [SimPy](https://simpy.readthedocs.io) machine-shop simulation
([`examples/simpy_machine_shop.py`](examples/simpy_machine_shop.py)):

| Output | cv | Verdict |
|---|---|---|
| total parts produced | 0.014 | **robust** |
| best machine · worst machine | 0.017 | **robust** |
| **gap between best and worst** | **0.31** | **fragile** |

The shop's total output is stable. The gap between machines is pure noise. Anyone looking at
one run and saying *"machine 7 is underperforming, investigate it"* is chasing a random seed.

**Averages hide fragility.** That alone is a reason to measure what you publish.

---

## Verified against simulations it was not written for

| Framework | Models | Result |
|---|---|---|
| [Mesa](https://github.com/projectmesa/mesa) | Schelling, WolfSheep, Boltzmann | works; WolfSheep's sheep population is fragile (cv 2.95 — usually extinct, occasionally not) |
| [SimPy](https://simpy.readthedocs.io) | machine shop | works; see above |
| [EoN](https://epidemicsonnetworks.readthedocs.io) | SIR on a network | works; epidemic duration is fragile (7.5 → 14.7) |
| [Omran](https://github.com/ahmedaly0904-bit64/Omran) | asabiyyah model | works; see above |

Examples: [`examples/`](examples/)

A control worth stating: the SimPy and Mesa examples reproduce byte-identically across
separate processes. That establishes that Omran's non-reproducibility is a bug in Omran,
and that Rasad's own pipeline is deterministic.

---

## The verdict is a convention. The numbers are the result.

The default cutoffs — 0.05 and 0.20 — **are a choice, not a theory**. An output at cv 0.21
reads *fragile*; raise the cutoff to 0.25 and the same data reads *wobbly*.

So every report prints the thresholds it used and labels them as a convention:

```
thresholds (a convention, not a rule): robust < 0.0500 <= wobbly <= 0.2000 < fragile
```

And they belong to the caller:

```python
rasad.measure(run, params={}, runs=100,
              thresholds={"robust": 0.01, "wobbly": 0.05})
```

**The real result is the interval.** `p05-p95 [7.46, 14.74]` says the duration may double,
without needing a word on top of it.

---

## Limitations

- **Only the seed varies.** Parameters are held fixed, so *"which parameter drives the
  result?"* is not answered yet. Sensitivity analysis is the next version.
- **Execution is sequential.** No parallelism.
- **One value per output name per run.** A model whose keys change between runs is rejected.

Accepted outputs: Python numbers, numpy scalars, 1-D numeric numpy arrays, lists and tuples.
**Booleans are always rejected** — alone or inside a list — because an average of ones and
zeros means nothing.

---

## Development

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pytest tests -v
```

71 tests · 97% coverage · linted with ruff

The statistics are tested against models whose answers are known analytically: a constant
must give a standard deviation of exactly zero; a random walk's divergence must grow as the
square root of time. Those tests caught real bugs — including a collapsed axis that would
have produced plausible, meaningless numbers.

---

## بالعربية

**رَصَد** أداة تقيس صلابة نتائج المحاكاة: أيُّ المخرجات خاصيةٌ في النموذج، وأيُّها أثرٌ للبذرة العشوائية.

تُنشر نتائج المحاكاة العشوائية غالبًا بلا حدود خطأ. يُقال «انهارت الحضارة في السنة ٢٤٠» دون
الإجابة على سؤالين: هل يظل الرقم ٢٤٠ لو تغيّرت البذرة؟ وهل هذه خاصية في النموذج أم صدفة في
تشغيلة واحدة؟ يجيب رَصَد عنهما بالقياس لا بالتقدير.

يوصّف المستخدم محاكاته بدالةٍ واحدة تستقبل المعاملات والبذرة وترجّع قاموس مخرجات. يشغّلها
رَصَد مرارًا ببذورٍ مختلفة، ثم يعرض لكل مخرَج متوسطه وانحرافه ومدى تسعين بالمئة وحكمًا —
**robust** أو **wobbly** أو **fragile** — مع منحنى يبيّن اتساع التباعد بين التشغيلات عبر الزمن.

طُبِّق على أربعة مشاريع لم يُكتب لأجلها، فكشف في أحدها — محاكاة لنظرية العصبية عند ابن خلدون —
أنها **لا تعيد إنتاج نتائجها بالبذرة نفسها**: تشغيلتان متطابقتان تفترقان عند السنة العشرين
بفارق فردٍ واحد، يصير مئاتٍ بحلول السنة المئة. وهذا انتشار الخطأ في صورته المقيسة.

وحدود التصنيف الافتراضية اصطلاحٌ لا قاعدة، ولذلك يعلنها كل تقرير ويتركها بيد المستخدم.
**النتيجة الحقيقية هي المدى**، لا الكلمة التي تعلوه.

---

## How this was built — full disclosure

Most of the code here was written by AI models under explicit delegation and human review.

| Stage | Owner |
|---|---|
| Specification and architecture | Ahmed, in dialogue with Claude (Opus 5) |
| **Test authoring** | Written into each task brief **before** implementation; the implementer was forbidden from altering a character |
| Implementation | DeepSeek V4 Flash, via `opencode` + AgentRouter — seven tasks |
| Review gates | Claude (Opus 5): every diff read, tests run independently of the implementer's claim |
| Decisions and merges | Ahmed — every commit after review |

**The ordering is what matters, not the tooling: the tests came first and were the
specification.** The model was never asked to write code and then write the thing that proves
it correct. It was given a written contract and held to it.

What the gates actually caught: a dead condition in a type check, a deprecated import, a
missing return annotation, unreadable number formatting. **No logic error got through** —
credit to the tests, not to the model.

And what none of them caught: an output that was constantly zero was classified *fragile*
when it was the most stable number in the report. Neither the reference models nor the review
found it — **the real data did, on the first run against Omran.**

That is the boundary. Tests prove the arithmetic is right; only real data reveals the case
nobody thought to write a test for.

---

## License

MIT
