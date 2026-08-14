"""Gráficos de replicação do M3E."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd

from .static import StaticSolution, solve_static


BLUE = "#156082"
ORANGE = "#E97132"
LIGHT_BLUE = "#00A6ED"
PURPLE = "#7030A0"
RED = "#FF0000"
GRID = "#D9D9D9"


def _window(data: pd.DataFrame, period_max: int | None) -> pd.DataFrame:
    if period_max is None:
        return data
    return data.loc[data["t"].between(-1, period_max)].copy()


def _style_axis(axis: plt.Axes) -> None:
    axis.grid(True, color=GRID, linewidth=0.8)
    axis.spines[["top", "right"]].set_visible(False)
    axis.set_xlabel("t")


def plot_gap(
    data: pd.DataFrame,
    period_max: int | None = 25,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    subset = _window(data, period_max)
    if ax is None:
        figure, ax = plt.subplots(figsize=(9, 5.2))
    else:
        figure = ax.figure
    ax.plot(subset["t"], subset["h"], color=BLUE, linewidth=2.2)
    ax.set_title("Hiato do Produto", fontweight="bold")
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=1))
    _style_axis(ax)
    return figure, ax


def plot_output(
    data: pd.DataFrame,
    period_max: int | None = 25,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    subset = _window(data, period_max)
    if ax is None:
        figure, ax = plt.subplots(figsize=(9, 5.2))
    else:
        figure = ax.figure
    ax.plot(subset["t"], subset["y"], label="y", color=BLUE, linewidth=2.2)
    ax.plot(
        subset["t"],
        subset["y_potential"],
        label="y*",
        color=ORANGE,
        linewidth=2.2,
    )
    ax.set_title("Produto efetivo e potencial", fontweight="bold")
    ax.legend(frameon=False, ncol=2)
    _style_axis(ax)
    return figure, ax


def plot_real_rate(
    data: pd.DataFrame,
    period_max: int | None = 25,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    subset = _window(data, period_max)
    if ax is None:
        figure, ax = plt.subplots(figsize=(9, 5.2))
    else:
        figure = ax.figure
    ax.plot(
        subset["t"],
        subset["r_expected"],
        label="r_exp",
        color=BLUE,
        linewidth=2.2,
    )
    ax.plot(subset["t"], subset["r_cb"], label="r_CB", color=ORANGE, linewidth=2.2)
    ax.set_title(
        "Taxa de juro real e estimativa do juro natural pelo BCB",
        fontweight="bold",
    )
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=2))
    ax.legend(frameon=False, ncol=2)
    _style_axis(ax)
    return figure, ax


def plot_inflation(
    data: pd.DataFrame,
    period_max: int | None = 25,
    ax: plt.Axes | None = None,
) -> tuple[plt.Figure, plt.Axes]:
    subset = _window(data, period_max)
    if ax is None:
        figure, ax = plt.subplots(figsize=(9, 5.2))
    else:
        figure = ax.figure
    ax.plot(subset["t"], subset["pi"], label="pi", color=LIGHT_BLUE, linewidth=2.2)
    ax.plot(
        subset["t"],
        subset["pi_expected"],
        label="pi_exp",
        color=PURPLE,
        linewidth=2.2,
    )
    ax.plot(
        subset["t"],
        subset["pi_long_run"],
        label="pi*",
        color=RED,
        linewidth=2.0,
        linestyle="--",
    )
    ax.set_title(
        "Inflação e expectativas de inflação, de curto e longo prazo",
        fontweight="bold",
    )
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=2))
    ax.legend(frameon=False, ncol=3)
    _style_axis(ax)
    return figure, ax


def plot_dynamic_all(
    data: pd.DataFrame,
    output_dir: str | Path,
    period_max: int | None = 25,
    dpi: int = 180,
) -> dict[str, Path]:
    """Grava os quatro gráficos da planilha e um painel consolidado."""

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    for name, function in (
        ("gap", plot_gap),
        ("output", plot_output),
        ("real_rate", plot_real_rate),
        ("inflation", plot_inflation),
    ):
        figure, _ = function(data, period_max=period_max)
        figure.tight_layout()
        path = destination / f"dynamic_{name}.png"
        figure.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
        plt.close(figure)
        paths[name] = path

    dashboard, axes = plt.subplots(2, 2, figsize=(14, 9))
    plot_gap(data, period_max, axes[0, 0])
    plot_output(data, period_max, axes[0, 1])
    plot_real_rate(data, period_max, axes[1, 0])
    plot_inflation(data, period_max, axes[1, 1])
    dashboard.suptitle("M3E dinâmico — replicação da planilha", fontsize=16, fontweight="bold")
    dashboard.tight_layout()
    dashboard_path = destination / "dynamic_dashboard.png"
    dashboard.savefig(
        dashboard_path, dpi=dpi, bbox_inches="tight", facecolor="white"
    )
    plt.close(dashboard)
    paths["dashboard"] = dashboard_path
    return paths


def plot_static_model(
    equilibrium_1: StaticSolution,
    equilibrium_2: StaticSolution,
    output_path: str | Path | None = None,
    dpi: int = 180,
) -> tuple[plt.Figure, np.ndarray]:
    """Reproduz a leitura gráfica IS–CP–RM dos dois equilíbrios."""

    solutions = (equilibrium_1, equilibrium_2)
    y_min = min(s.values[0] for s in solutions) - 0.05
    y_max = max(s.values[0] for s in solutions) + 0.05
    y_grid = np.linspace(y_min, y_max, 300)
    figure, axes = plt.subplots(1, 2, figsize=(13, 5.2))

    for idx, solution in enumerate(solutions, start=1):
        p = solution.parameters
        color = BLUE if idx == 1 else LIGHT_BLUE
        r_is = (p.y_autonomous - y_grid) / p.gamma
        axes[0].plot(y_grid, r_is, color=color, linewidth=2.2, label=f"IS {idx}")
        axes[0].scatter(solution.values[0], solution.values[3], color=color, s=45)

        pi_cp = p.pi_long_run + p.alpha / (1.0 - p.theta) * (
            y_grid - p.y_potential
        )
        r_from_is = (p.y_autonomous - y_grid) / p.gamma
        pi_rm = (
            p.pi_target
            + (r_from_is - p.r_cb) / p.phi_pi
            - (1.0 - p.theta) * p.pi_long_run
        ) / p.theta
        axes[1].plot(
            y_grid,
            pi_cp,
            color=RED if idx == 1 else "#FF8080",
            linewidth=2.2,
            label=f"CP {idx}",
        )
        axes[1].plot(
            y_grid,
            pi_rm,
            color="#00A65A" if idx == 1 else "#66CC99",
            linewidth=2.2,
            label=f"RM {idx}",
        )
        axes[1].scatter(solution.values[0], solution.values[2], color=color, s=45)

    axes[0].axvline(equilibrium_1.parameters.y_potential, color="#999999", linestyle=":")
    axes[0].set_title("Curva IS", fontweight="bold")
    axes[0].set_xlabel("y")
    axes[0].set_ylabel("r esperado")
    axes[0].yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=1))
    axes[0].legend(frameon=False)
    axes[0].grid(True, color=GRID)

    axes[1].axvline(equilibrium_1.parameters.y_potential, color="#999999", linestyle=":")
    axes[1].axhline(equilibrium_1.parameters.pi_target, color="#999999", linestyle=":")
    axes[1].set_title("Curva de Phillips e regra monetária", fontweight="bold")
    axes[1].set_xlabel("y")
    axes[1].set_ylabel("inflação")
    axes[1].yaxis.set_major_formatter(mtick.PercentFormatter(1.0, decimals=1))
    axes[1].legend(frameon=False, ncol=2)
    axes[1].grid(True, color=GRID)

    figure.suptitle("M3E estático — equilíbrios 1 e 2", fontsize=15, fontweight="bold")
    figure.tight_layout()
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        figure.savefig(path, dpi=dpi, bbox_inches="tight", facecolor="white")
    return figure, axes

