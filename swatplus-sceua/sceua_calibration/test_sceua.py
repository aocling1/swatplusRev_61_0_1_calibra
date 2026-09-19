"""Basic tests for the compact SCE-UA implementation."""

from __future__ import annotations

import unittest

import numpy as np

from sceua import sceua


class SCEUATest(unittest.TestCase):
    def test_finds_quadratic_minimum(self) -> None:
        target = np.array([0.25, -0.4])

        def objective(parameters: np.ndarray) -> float:
            return float(np.sum((parameters - target) ** 2))

        result = sceua(
            objective,
            bounds=[(-2.0, 2.0), (-2.0, 2.0)],
            max_evaluations=1200,
            seed=7,
            tolerance=1e-9,
        )
        self.assertLess(result.fun, 1e-4)
        np.testing.assert_allclose(result.x, target, atol=0.03)

    def test_rejects_invalid_bounds(self) -> None:
        with self.assertRaises(ValueError):
            sceua(lambda values: float(values[0]), [(1.0, 1.0)])


if __name__ == "__main__":
    unittest.main()

