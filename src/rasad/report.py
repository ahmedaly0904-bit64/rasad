"""Presentation of a measurement, and nothing else.

This is the only module concerned with how a measurement is shown to a
human. No assumption about the command line may leak below it: a future
web layer becomes a second view over the same data, built from the same
:class:`Report`.
"""

import math
from typing import Any

import plotly.graph_objects as go

# Deterministic rendering so two runs with the same seeds stay byte-identical:
# fixed decimals for magnitudes large enough to keep them, significant digits
# for the rest.
_VALUE_DECIMALS = 2
_RATIO_DECIMALS = 4


def _fmt(value: float) -> str:
    """Format a magnitude — inf-safe, and never rounds a small value away.

    Exact zero and magnitudes of at least 0.005 (the point past which two
    decimals can no longer round to ``0.00``) render with grouped thousands
    and two fixed decimals; smaller magnitudes render with three significant
    digits, e.g. ``0.001`` or ``1.2e-09``, so they stay visible.
    """
    if math.isinf(value):
        return "inf"
    if value == 0 or abs(value) >= 0.005:
        return f"{value:,.{_VALUE_DECIMALS}f}"
    return f"{value:.3g}"


def _fmt_ratio(value: float) -> str:
    """Format a dimensionless ratio, which needs more decimals than a magnitude."""
    if math.isinf(value):
        return "inf"
    return f"{value:.{_RATIO_DECIMALS}f}"


class Report:
    """The result of measuring one model.

    Attributes
    ----------
    scalars
        Output name to the summary dict from :func:`rasad.analyzer.summarize`
        plus a ``variability`` key holding the string from
        :func:`rasad.analyzer.classify`.
    series
        Output name to the divergence curve from
        :func:`rasad.analyzer.divergence`.
    runs
        How many runs the report was built from.
    thresholds
        The classification cutoffs that were used, as a plain dict of
        floats (see :data:`rasad.analyzer.THRESHOLDS`).
    """

    def __init__(
        self,
        scalars: dict[str, dict[str, Any]],
        series: dict[str, list[float]],
        runs: int,
        thresholds: dict[str, float],
    ) -> None:
        self.scalars = scalars
        self.series = series
        self.runs = runs
        self.thresholds = thresholds

    def summary(self) -> str:
        """Render the report as a plain-text table.

        Returns
        -------
        str
            A header with the run count, one row per scalar output
            (name, mean, standard deviation, coefficient of variation,
            p05-p95 interval, variability) and, when present, one
            line per series showing how the divergence grew.
        """
        lines = [f"Rasad report of {self.runs} runs"]
        lines.append(
            f"thresholds (a convention, not a rule): low < "
            f"{_fmt_ratio(self.thresholds['low'])} <= moderate <= "
            f"{_fmt_ratio(self.thresholds['moderate'])} < high"
        )

        if self.scalars:
            lines.append("Scalar outputs:")
            for name, stats in self.scalars.items():
                lines.append(
                    f"  {name}: mean {_fmt(stats['mean'])} | "
                    f"std {_fmt(stats['std'])} | "
                    f"cv {_fmt_ratio(stats['cv'])} | "
                    f"p05-p95 [{_fmt(stats['p05'])}, {_fmt(stats['p95'])}] | "
                    f"variability: {stats['variability']}"
                )

        if self.series:
            lines.append("Series:")
            for name, curve in self.series.items():
                lines.append(
                    f"  {name}: divergence from {_fmt(curve[0])} to "
                    f"{_fmt(curve[-1])} over {len(curve)} steps"
                )

        return "\n".join(lines)

    def plot(self) -> go.Figure:
        """Render the report as a divergence chart.

        Returns
        -------
        plotly.graph_objects.Figure
            One line trace per series in :attr:`series`, x being the
            time step and y the standard deviation between runs.

        Raises
        ------
        ValueError
            When there is no time series to plot.
        """
        if not self.series:
            raise ValueError("no time series to plot")

        fig = go.Figure()
        for name, curve in self.series.items():
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(curve))),
                    y=curve,
                    mode="lines",
                    name=name,
                )
            )

        fig.update_layout(
            title=f"Rasad report of {self.runs} runs",
            xaxis_title="time step",
            yaxis_title="standard deviation between runs",
        )
        return fig
