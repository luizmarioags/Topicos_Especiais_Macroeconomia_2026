from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from m3e import (
    dynamic_reduced_form,
    excel_dynamic_shocks,
    excel_static_scenarios,
    simulate_dynamic,
    simulate_dynamic_matrix,
    solve_static,
)


ROOT = Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "reference"


class StaticReplicationTest(unittest.TestCase):
    def test_excel_equilibria(self) -> None:
        parameters_1, parameters_2 = excel_static_scenarios()
        solution_1 = solve_static(parameters_1)
        solution_2 = solve_static(parameters_2)
        expected_1 = np.array([1.0, 0.035, 0.035, 0.05])
        expected_2 = np.array(
            [
                1.0756756756756758,
                0.043108108108108105,
                0.06202702702702702,
                0.06216216216216216,
            ]
        )
        np.testing.assert_allclose(solution_1.values, expected_1, atol=1e-14, rtol=0)
        np.testing.assert_allclose(solution_2.values, expected_2, atol=1e-14, rtol=0)
        self.assertLess(np.abs(solution_1.residual).max(), 1e-14)
        self.assertLess(np.abs(solution_2.residual).max(), 1e-14)


class DynamicReplicationTest(unittest.TestCase):
    def test_recursive_and_matrix_simulations_coincide(self) -> None:
        shocks = excel_dynamic_shocks(509)
        recursive = simulate_dynamic(shocks=shocks, horizon=509)
        matrix = simulate_dynamic_matrix(shocks=shocks, horizon=509)
        columns = [
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
        ]
        np.testing.assert_allclose(
            recursive[columns].to_numpy(),
            matrix[columns].to_numpy(),
            atol=5e-14,
            rtol=0,
        )

    def test_reference_csv(self) -> None:
        expected = pd.read_csv(REFERENCE / "dynamic_excel_reference.csv")
        actual = simulate_dynamic(shocks=excel_dynamic_shocks(509), horizon=509)
        expected = expected[actual.columns]
        np.testing.assert_allclose(
            actual.drop(columns="t").to_numpy(),
            expected.drop(columns="t").to_numpy(),
            atol=2e-13,
            rtol=0,
        )
        np.testing.assert_array_equal(actual["t"].to_numpy(), expected["t"].to_numpy())

    def test_reduced_form_dimensions(self) -> None:
        matrices = dynamic_reduced_form()
        self.assertEqual(np.asarray(matrices["A"]).shape, (11, 5))
        self.assertEqual(np.asarray(matrices["B"]).shape, (11, 7))
        self.assertEqual(np.asarray(matrices["F"]).shape, (5, 5))
        self.assertEqual(np.asarray(matrices["G"]).shape, (5, 7))


if __name__ == "__main__":
    unittest.main()
