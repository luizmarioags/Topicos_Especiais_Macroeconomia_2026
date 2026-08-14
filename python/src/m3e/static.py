"""Núcleo linear do M3E estático.

O ordenamento das incógnitas reproduz a planilha Excel:
``[y, pi_expected, pi, r_expected]``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Mapping

import numpy as np
import pandas as pd


STATIC_VARIABLES = ("y", "pi_expected", "pi", "r_expected")


@dataclass(frozen=True)
class StaticParameters:
    """Parâmetros e variáveis exógenas do equilíbrio estático."""

    y_potential: float = 1.0
    y_autonomous: float = 1.1
    r_cb: float = 0.05
    pi_long_run: float = 0.035
    pi_target: float = 0.035
    gamma: float = 2.0
    theta: float = 0.3
    alpha: float = 0.25
    phi_pi: float = 1.5

    def __post_init__(self) -> None:
        if self.gamma <= 0:
            raise ValueError("gamma deve ser estritamente positivo")
        if not 0 <= self.theta < 1:
            raise ValueError("theta deve pertencer ao intervalo [0, 1)")
        if self.alpha <= 0:
            raise ValueError("alpha deve ser estritamente positivo")
        if self.phi_pi < 0:
            raise ValueError("phi_pi não pode ser negativo")

    @property
    def r_natural(self) -> float:
        return (self.y_autonomous - self.y_potential) / self.gamma

    def with_changes(self, **changes: float) -> "StaticParameters":
        return replace(self, **changes)

    def as_dict(self) -> dict[str, float]:
        values = asdict(self)
        values["r_natural"] = self.r_natural
        return values


@dataclass(frozen=True)
class StaticSolution:
    """Solução, matriz inversa e diagnósticos de um equilíbrio."""

    parameters: StaticParameters
    coefficients: np.ndarray
    exogenous: np.ndarray
    inverse: np.ndarray
    values: np.ndarray

    def as_dict(self) -> dict[str, float]:
        return dict(zip(STATIC_VARIABLES, self.values, strict=True))

    def as_series(self) -> pd.Series:
        return pd.Series(self.as_dict(), name="equilibrium")

    @property
    def output_gap(self) -> float:
        return float(self.values[0] - self.parameters.y_potential)

    @property
    def nominal_rate_ex_ante(self) -> float:
        return float(self.values[3] + self.values[1])

    @property
    def nominal_rate_ex_post(self) -> float:
        return float(self.values[3] + self.values[2])

    @property
    def residual(self) -> np.ndarray:
        return self.coefficients @ self.values - self.exogenous


def _coerce_parameters(
    parameters: StaticParameters | Mapping[str, float] | None,
) -> StaticParameters:
    if parameters is None:
        return StaticParameters()
    if isinstance(parameters, StaticParameters):
        return parameters
    return StaticParameters(**dict(parameters))


def static_matrices(
    parameters: StaticParameters | Mapping[str, float] | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Constrói a matriz de coeficientes ``A`` e o vetor exógeno ``b``.

    O sistema é ``A @ x = b``, com
    ``x = [y, pi_expected, pi, r_expected]``.
    """

    p = _coerce_parameters(parameters)
    coefficients = np.array(
        [
            [1.0, 0.0, 0.0, p.gamma],
            [0.0, 1.0, -p.theta, 0.0],
            [-p.alpha, -1.0, 1.0, 0.0],
            [0.0, -p.phi_pi, 0.0, 1.0],
        ],
        dtype=float,
    )
    exogenous = np.array(
        [
            p.y_autonomous,
            (1.0 - p.theta) * p.pi_long_run,
            -p.alpha * p.y_potential,
            p.r_cb - p.phi_pi * p.pi_target,
        ],
        dtype=float,
    )
    return coefficients, exogenous


def solve_static(
    parameters: StaticParameters | Mapping[str, float] | None = None,
) -> StaticSolution:
    """Resolve o equilíbrio estático e devolve todos os objetos matriciais."""

    p = _coerce_parameters(parameters)
    coefficients, exogenous = static_matrices(p)
    inverse = np.linalg.inv(coefficients)
    values = inverse @ exogenous
    return StaticSolution(p, coefficients, exogenous, inverse, values)


def compare_static(
    base: StaticSolution | StaticParameters | Mapping[str, float] | None = None,
    scenario: StaticSolution | StaticParameters | Mapping[str, float] | None = None,
) -> pd.DataFrame:
    """Compara dois equilíbrios e calcula desvios absolutos e relativos."""

    base_solution = base if isinstance(base, StaticSolution) else solve_static(base)
    scenario_solution = (
        scenario if isinstance(scenario, StaticSolution) else solve_static(scenario)
    )
    base_values = base_solution.values
    scenario_values = scenario_solution.values
    with np.errstate(divide="ignore", invalid="ignore"):
        relative = np.where(base_values != 0, scenario_values / base_values - 1.0, np.nan)
    return pd.DataFrame(
        {
            "variable": STATIC_VARIABLES,
            "equilibrium_1": base_values,
            "equilibrium_2": scenario_values,
            "absolute_deviation": scenario_values - base_values,
            "relative_deviation": relative,
        }
    )


def excel_static_scenarios() -> tuple[StaticParameters, StaticParameters]:
    """Retorna as duas colunas de parâmetros da planilha estática."""

    equilibrium_1 = StaticParameters()
    equilibrium_2 = equilibrium_1.with_changes(y_autonomous=1.2)
    return equilibrium_1, equilibrium_2

