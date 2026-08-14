"""Modelo Macroeconômico de 3 Equações (M3E)."""

from .dynamic import (
    DYNAMIC_OUTPUTS,
    DYNAMIC_STATE,
    DYNAMIC_SHOCKS,
    DynamicInitial,
    DynamicParameters,
    dynamic_reduced_form,
    excel_dynamic_shocks,
    simulate_dynamic,
    simulate_dynamic_matrix,
)
from .plots import (
    plot_dynamic_all,
    plot_gap,
    plot_inflation,
    plot_output,
    plot_real_rate,
    plot_static_model,
)
from .static import (
    STATIC_VARIABLES,
    StaticParameters,
    StaticSolution,
    compare_static,
    excel_static_scenarios,
    solve_static,
    static_matrices,
)

__all__ = [
    "DYNAMIC_OUTPUTS",
    "DYNAMIC_SHOCKS",
    "DYNAMIC_STATE",
    "STATIC_VARIABLES",
    "DynamicInitial",
    "DynamicParameters",
    "StaticParameters",
    "StaticSolution",
    "compare_static",
    "dynamic_reduced_form",
    "excel_dynamic_shocks",
    "excel_static_scenarios",
    "plot_dynamic_all",
    "plot_gap",
    "plot_inflation",
    "plot_output",
    "plot_real_rate",
    "plot_static_model",
    "simulate_dynamic",
    "simulate_dynamic_matrix",
    "solve_static",
    "static_matrices",
]

__version__ = "0.1.0"

