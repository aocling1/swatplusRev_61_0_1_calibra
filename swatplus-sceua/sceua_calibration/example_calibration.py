"""Runnable example for the minimal SCE-UA implementation."""

from __future__ import annotations

import numpy as np

from sceua import sceua


TIMES = np.arange(1.0, 13.0)
OBSERVED = np.array(
    [0.31, 0.55, 0.74, 0.89, 1.01, 1.10, 1.17, 1.23, 1.27, 1.30, 1.33, 1.35]
)


def simulate(parameters: np.ndarray) -> np.ndarray:
    """A small saturation-curve model used only for demonstration."""
    scale, rate = parameters
    return scale * (1.0 - np.exp(-rate * TIMES))


def rmse_objective(parameters: np.ndarray) -> float:
    residuals = simulate(parameters) - OBSERVED
    return float(np.sqrt(np.mean(residuals**2)))


def main() -> None:
    result = sceua(
        rmse_objective,
        bounds=[(0.5, 2.0), (0.01, 1.0)],
        max_evaluations=1200,
        seed=42,
    )
    print("Best parameters:", result.x)
    print("Best RMSE:", result.fun)
    print("Evaluations:", result.n_evaluations)
    print("Shuffles:", result.n_shuffles)
    print("Converged:", result.converged)


if __name__ == "__main__":
    main()

