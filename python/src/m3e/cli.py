"""Linha de comando para gerar integralmente o pacote de replicação."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .dynamic import dynamic_reduced_form, excel_dynamic_shocks, simulate_dynamic
from .plots import plot_dynamic_all, plot_static_model
from .static import STATIC_VARIABLES, compare_static, excel_static_scenarios, solve_static


def _save_matrix(path: Path, matrix: np.ndarray, rows: list[str], cols: list[str]) -> None:
    pd.DataFrame(matrix, index=rows, columns=cols).to_csv(path, index=True)


def generate_all(output_dir: str | Path) -> dict[str, str]:
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    base_params, shock_params = excel_static_scenarios()
    base = solve_static(base_params)
    shock = solve_static(shock_params)
    _save_matrix(
        destination / "static_A.csv",
        base.coefficients,
        ["IS", "expectations", "Phillips", "monetary_rule"],
        list(STATIC_VARIABLES),
    )
    _save_matrix(
        destination / "static_A_inverse.csv",
        base.inverse,
        list(STATIC_VARIABLES),
        ["IS", "expectations", "Phillips", "monetary_rule"],
    )
    compare_static(base, shock).to_csv(destination / "static_comparison.csv", index=False)
    figure, _ = plot_static_model(base, shock, destination / "static_model.png")
    plt.close(figure)

    trajectory = simulate_dynamic(
        shocks=excel_dynamic_shocks(horizon=509), horizon=509
    )
    trajectory.to_csv(destination / "dynamic_simulation.csv", index=False)
    plot_dynamic_all(trajectory, destination, period_max=25)

    matrices = dynamic_reduced_form()
    _save_matrix(
        destination / "dynamic_A.csv",
        np.asarray(matrices["A"]),
        list(matrices["output_names"]),
        list(matrices["state_names"]),
    )
    _save_matrix(
        destination / "dynamic_B.csv",
        np.asarray(matrices["B"]),
        list(matrices["output_names"]),
        list(matrices["shock_names"]),
    )
    _save_matrix(
        destination / "dynamic_F.csv",
        np.asarray(matrices["F"]),
        list(matrices["state_names"]),
        list(matrices["state_names"]),
    )
    _save_matrix(
        destination / "dynamic_G.csv",
        np.asarray(matrices["G"]),
        list(matrices["state_names"]),
        list(matrices["shock_names"]),
    )
    metadata = {
        "static_residual_max_abs": float(
            max(np.abs(base.residual).max(), np.abs(shock.residual).max())
        ),
        "dynamic_rows": int(len(trajectory)),
        "dynamic_first_period": int(trajectory["t"].min()),
        "dynamic_last_period": int(trajectory["t"].max()),
    }
    (destination / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    return {path.name: str(path) for path in sorted(destination.iterdir())}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default="outputs/python")
    args = parser.parse_args()
    generate_all(args.output_dir)


if __name__ == "__main__":
    main()

