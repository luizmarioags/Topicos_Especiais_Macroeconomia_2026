"""M3E dinâmico em forma recursiva e em forma reduzida matricial."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence

import numpy as np
import pandas as pd


DYNAMIC_STATE = ("y", "y_potential", "y_autonomous", "r_cb", "pi")
DYNAMIC_OUTPUTS = (
    "h",
    "y",
    "y_potential",
    "y_autonomous",
    "r_expected",
    "r_cb",
    "r_natural",
    "pi",
    "pi_expected",
    "pi_long_run",
    "pi_target",
)
DYNAMIC_SHOCKS = (
    "demand",
    "is",
    "inflation",
    "potential",
    "policy",
    "expectations_short",
    "expectations_long",
)
STATE_ROWS = np.array([1, 2, 3, 5, 7], dtype=int)


@dataclass(frozen=True)
class DynamicParameters:
    gamma: float = 2.0
    theta: float = 0.3
    alpha: float = 0.25
    phi_pi: float = 1.5
    phi_y: float = 0.25
    chi: float = 0.1
    eta: float = 0.05
    pi_target: float = 0.035

    def __post_init__(self) -> None:
        if self.gamma <= 0:
            raise ValueError("gamma deve ser estritamente positivo")
        if self.alpha <= 0:
            raise ValueError("alpha deve ser estritamente positivo")
        for name in ("theta", "chi", "eta"):
            value = getattr(self, name)
            if not 0 <= value <= 1:
                raise ValueError(f"{name} deve pertencer ao intervalo [0, 1]")
        if self.phi_pi < 0 or self.phi_y < 0:
            raise ValueError("phi_pi e phi_y não podem ser negativos")

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class DynamicInitial:
    """Condição inicial observada em ``t = -1``."""

    y: float = 1.0
    y_potential: float = 1.0
    y_autonomous: float = 1.1
    r_expected: float = 0.05
    r_cb: float = 0.05
    pi: float = 0.035
    pi_expected: float = 0.035
    pi_long_run: float = 0.035

    def state_vector(self) -> np.ndarray:
        return np.array(
            [self.y, self.y_potential, self.y_autonomous, self.r_cb, self.pi],
            dtype=float,
        )


def _coerce_parameters(
    parameters: DynamicParameters | Mapping[str, float] | None,
) -> DynamicParameters:
    if parameters is None:
        return DynamicParameters()
    if isinstance(parameters, DynamicParameters):
        return parameters
    return DynamicParameters(**dict(parameters))


def _coerce_initial(
    initial: DynamicInitial | Mapping[str, float] | None,
) -> DynamicInitial:
    if initial is None:
        return DynamicInitial()
    if isinstance(initial, DynamicInitial):
        return initial
    return DynamicInitial(**dict(initial))


def _transition_from_vectors(
    previous_state: Sequence[float],
    shock_vector: Sequence[float],
    p: DynamicParameters,
) -> np.ndarray:
    y_lag, y_potential_lag, y_autonomous_lag, r_cb_lag, pi_lag = map(
        float, previous_state
    )
    (
        shock_demand,
        shock_is,
        shock_inflation,
        shock_potential,
        shock_policy,
        shock_expectations_short,
        shock_expectations_long,
    ) = map(float, shock_vector)

    y_autonomous = y_autonomous_lag + shock_demand
    y_potential = (
        (1.0 - p.eta) * y_potential_lag
        + p.eta * y_lag
        + shock_potential
    )
    r_cb = r_cb_lag + p.phi_y * (y_lag - y_potential_lag) + shock_policy
    pi_long_run = (
        (1.0 - p.chi) * p.pi_target
        + p.chi * pi_lag
        + shock_expectations_long
    )
    pi_expected = (
        p.theta * pi_lag
        + (1.0 - p.theta) * pi_long_run
        + shock_expectations_short
    )
    r_expected = r_cb + p.phi_pi * (pi_expected - p.pi_target)
    y = y_autonomous - p.gamma * r_expected + shock_is
    h = y - y_potential
    pi = pi_expected + p.alpha * h + shock_inflation
    r_natural = (y_autonomous - y_potential) / p.gamma

    return np.array(
        [
            h,
            y,
            y_potential,
            y_autonomous,
            r_expected,
            r_cb,
            r_natural,
            pi,
            pi_expected,
            pi_long_run,
            p.pi_target,
        ],
        dtype=float,
    )


def dynamic_reduced_form(
    parameters: DynamicParameters | Mapping[str, float] | None = None,
) -> dict[str, object]:
    """Obtém a forma afim ``z_t = c + A s_(t-1) + B eps_t``.

    ``s`` segue :data:`DYNAMIC_STATE`, ``z`` segue :data:`DYNAMIC_OUTPUTS` e
    ``eps`` segue :data:`DYNAMIC_SHOCKS`. A matriz de transição de estado é
    formada pelas linhas de ``A`` indicadas por ``state_rows``.
    """

    p = _coerce_parameters(parameters)
    zero_state = np.zeros(len(DYNAMIC_STATE), dtype=float)
    zero_shocks = np.zeros(len(DYNAMIC_SHOCKS), dtype=float)
    constant = _transition_from_vectors(zero_state, zero_shocks, p)
    observation_state = np.column_stack(
        [
            _transition_from_vectors(np.eye(len(DYNAMIC_STATE))[j], zero_shocks, p)
            - constant
            for j in range(len(DYNAMIC_STATE))
        ]
    )
    observation_shocks = np.column_stack(
        [
            _transition_from_vectors(zero_state, np.eye(len(DYNAMIC_SHOCKS))[j], p)
            - constant
            for j in range(len(DYNAMIC_SHOCKS))
        ]
    )
    return {
        "output_names": DYNAMIC_OUTPUTS,
        "state_names": DYNAMIC_STATE,
        "shock_names": DYNAMIC_SHOCKS,
        "constant": constant,
        "A": observation_state,
        "B": observation_shocks,
        "state_rows": STATE_ROWS.copy(),
        "state_constant": constant[STATE_ROWS],
        "F": observation_state[STATE_ROWS, :],
        "G": observation_shocks[STATE_ROWS, :],
    }


def _assign_shock_column(
    target: pd.Series, value: object, horizon: int, name: str
) -> None:
    if np.isscalar(value):
        target.loc[0] = float(value)
        return
    if isinstance(value, Mapping):
        for period, amount in value.items():
            period_int = int(period)
            if 0 <= period_int <= horizon:
                target.loc[period_int] = float(amount)
        return
    array = np.asarray(list(value), dtype=float)
    if len(array) != horizon + 1:
        raise ValueError(
            f"choque '{name}' deve ter {horizon + 1} elementos; recebeu {len(array)}"
        )
    target.loc[:] = array


def normalise_shocks(
    shocks: pd.DataFrame | Mapping[str, object] | None,
    horizon: int,
) -> pd.DataFrame:
    """Normaliza diferentes especificações de choque para um quadro completo."""

    if horizon < 0:
        raise ValueError("horizon deve ser maior ou igual a zero")
    result = pd.DataFrame(0.0, index=range(horizon + 1), columns=DYNAMIC_SHOCKS)
    result.index.name = "t"
    if shocks is None:
        return result
    if isinstance(shocks, pd.DataFrame):
        source = shocks.copy()
        if "t" in source.columns:
            source = source.set_index("t")
        unknown = set(source.columns) - set(DYNAMIC_SHOCKS)
        if unknown:
            raise ValueError(f"choques desconhecidos: {sorted(unknown)}")
        for name in source.columns:
            for period, amount in source[name].dropna().items():
                period_int = int(period)
                if 0 <= period_int <= horizon:
                    result.loc[period_int, name] = float(amount)
        return result
    unknown = set(shocks) - set(DYNAMIC_SHOCKS)
    if unknown:
        raise ValueError(f"choques desconhecidos: {sorted(unknown)}")
    for name, value in shocks.items():
        _assign_shock_column(result[name], value, horizon, name)
    return result


def excel_dynamic_shocks(horizon: int = 509) -> pd.DataFrame:
    """Choque permanente de 1% em ``y_autonomous`` aplicado em ``t=0``."""

    return normalise_shocks({"demand": {0: 0.01}}, horizon)


def _initial_row(
    initial: DynamicInitial, p: DynamicParameters
) -> dict[str, float | int]:
    r_natural = (initial.y_autonomous - initial.y_potential) / p.gamma
    return {
        "t": -1,
        "h": initial.y - initial.y_potential,
        "y": initial.y,
        "y_potential": initial.y_potential,
        "y_autonomous": initial.y_autonomous,
        "r_expected": initial.r_expected,
        "r_cb": initial.r_cb,
        "r_natural": r_natural,
        "pi": initial.pi,
        "pi_expected": initial.pi_expected,
        "pi_long_run": initial.pi_long_run,
        "pi_target": p.pi_target,
    }


def _append_parameters(frame: pd.DataFrame, p: DynamicParameters) -> pd.DataFrame:
    result = frame.copy()
    for name in ("gamma", "theta", "alpha", "phi_pi", "phi_y", "chi", "eta"):
        result[name] = getattr(p, name)
    return result


def simulate_dynamic(
    parameters: DynamicParameters | Mapping[str, float] | None = None,
    initial: DynamicInitial | Mapping[str, float] | None = None,
    shocks: pd.DataFrame | Mapping[str, object] | None = None,
    horizon: int = 509,
    include_parameters: bool = True,
) -> pd.DataFrame:
    """Simula o sistema recursivo exatamente na ordem usada pelo Excel."""

    p = _coerce_parameters(parameters)
    init = _coerce_initial(initial)
    shock_frame = normalise_shocks(shocks, horizon)
    rows: list[dict[str, float | int]] = [_initial_row(init, p)]
    previous_state = init.state_vector()
    for period in range(horizon + 1):
        shock_vector = shock_frame.loc[period, list(DYNAMIC_SHOCKS)].to_numpy(float)
        output = _transition_from_vectors(previous_state, shock_vector, p)
        row = {"t": period}
        row.update(dict(zip(DYNAMIC_OUTPUTS, output, strict=True)))
        rows.append(row)
        previous_state = output[STATE_ROWS]
    result = pd.DataFrame(rows)
    return _append_parameters(result, p) if include_parameters else result


def simulate_dynamic_matrix(
    parameters: DynamicParameters | Mapping[str, float] | None = None,
    initial: DynamicInitial | Mapping[str, float] | None = None,
    shocks: pd.DataFrame | Mapping[str, object] | None = None,
    horizon: int = 509,
    include_parameters: bool = True,
) -> pd.DataFrame:
    """Simula a mesma trajetória usando exclusivamente a forma reduzida."""

    p = _coerce_parameters(parameters)
    init = _coerce_initial(initial)
    shock_frame = normalise_shocks(shocks, horizon)
    matrices = dynamic_reduced_form(p)
    constant = np.asarray(matrices["constant"])
    a_matrix = np.asarray(matrices["A"])
    b_matrix = np.asarray(matrices["B"])
    rows: list[dict[str, float | int]] = [_initial_row(init, p)]
    previous_state = init.state_vector()
    for period in range(horizon + 1):
        shock_vector = shock_frame.loc[period, list(DYNAMIC_SHOCKS)].to_numpy(float)
        output = constant + a_matrix @ previous_state + b_matrix @ shock_vector
        row = {"t": period}
        row.update(dict(zip(DYNAMIC_OUTPUTS, output, strict=True)))
        rows.append(row)
        previous_state = output[STATE_ROWS]
    result = pd.DataFrame(rows)
    return _append_parameters(result, p) if include_parameters else result

