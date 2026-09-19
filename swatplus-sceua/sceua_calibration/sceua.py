"""A compact implementation of the SCE-UA global optimization algorithm.

The optimizer minimizes a user-supplied objective function. It is intended as
an understandable research starting point rather than a drop-in replacement
for a mature calibration package.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

import numpy as np


ArrayLike = Sequence[float] | np.ndarray


@dataclass(frozen=True)
class SCEUAResult:
    """Result returned by :func:`sceua`."""

    x: np.ndarray
    fun: float
    n_evaluations: int
    n_shuffles: int
    converged: bool
    history: tuple[float, ...]


def _validate_bounds(bounds: Sequence[tuple[float, float]]) -> tuple[np.ndarray, np.ndarray]:
    if not bounds:
        raise ValueError("bounds must contain at least one (lower, upper) pair")
    lower = np.asarray([item[0] for item in bounds], dtype=float)
    upper = np.asarray([item[1] for item in bounds], dtype=float)
    if not np.all(np.isfinite(lower)) or not np.all(np.isfinite(upper)):
        raise ValueError("all bounds must be finite")
    if np.any(lower >= upper):
        raise ValueError("every lower bound must be smaller than its upper bound")
    return lower, upper


def _ranked_sample(rng: np.random.Generator, size: int, count: int) -> np.ndarray:
    """Select indices without replacement while favoring better ranks."""
    ranks = np.arange(size, 0, -1, dtype=float)
    probabilities = ranks / ranks.sum()
    return np.sort(rng.choice(size, size=count, replace=False, p=probabilities))


def sceua(
    objective: Callable[[np.ndarray], float],
    bounds: Sequence[tuple[float, float]],
    *,
    x0: ArrayLike | None = None,
    n_complexes: int | None = None,
    complex_size: int | None = None,
    max_evaluations: int = 2000,
    evolution_steps: int | None = None,
    seed: int | None = None,
    tolerance: float = 1e-6,
    convergence_window: int = 8,
) -> SCEUAResult:
    """Minimize ``objective`` with a simplified SCE-UA search.

    Parameters
    ----------
    objective:
        Function accepting a one-dimensional NumPy array and returning a
        finite scalar loss. Smaller values are better.
    bounds:
        One ``(lower, upper)`` pair per parameter.
    x0:
        Optional initial parameter vector.
    n_complexes, complex_size:
        Population layout. Defaults are based on the number of parameters.
    max_evaluations:
        Maximum number of objective-function calls.
    evolution_steps:
        Number of competitive-complex evolution steps before shuffling.
    seed:
        Random seed for reproducible runs.
    tolerance, convergence_window:
        Stop when the relative improvement of the best loss over the window
        is no greater than ``tolerance``.
    """
    lower, upper = _validate_bounds(bounds)
    n_parameters = lower.size
    n_complexes = n_complexes or max(2, min(5, n_parameters))
    complex_size = complex_size or (2 * n_parameters + 1)
    evolution_steps = evolution_steps or complex_size

    if n_complexes < 1 or complex_size < n_parameters + 1:
        raise ValueError("complex_size must be at least n_parameters + 1")
    population_size = n_complexes * complex_size
    if max_evaluations < population_size:
        raise ValueError("max_evaluations must cover the initial population")
    if convergence_window < 2:
        raise ValueError("convergence_window must be at least 2")

    rng = np.random.default_rng(seed)
    population = rng.uniform(lower, upper, size=(population_size, n_parameters))
    if x0 is not None:
        initial = np.asarray(x0, dtype=float)
        if initial.shape != (n_parameters,):
            raise ValueError("x0 must have one value per parameter")
        population[0] = np.clip(initial, lower, upper)

    evaluations = 0

    def evaluate(point: np.ndarray) -> float:
        nonlocal evaluations
        value = float(objective(point.copy()))
        evaluations += 1
        if not np.isfinite(value):
            return float("inf")
        return value

    scores = np.asarray([evaluate(point) for point in population], dtype=float)
    history: list[float] = []
    shuffles = 0
    converged = False

    while evaluations < max_evaluations:
        order = np.argsort(scores)
        population = population[order]
        scores = scores[order]
        history.append(float(scores[0]))

        if len(history) >= convergence_window:
            earlier = history[-convergence_window]
            current = history[-1]
            scale = max(1.0, abs(earlier))
            if abs(earlier - current) / scale <= tolerance:
                converged = True
                break

        complexes: list[np.ndarray] = []
        complex_scores: list[np.ndarray] = []
        for complex_index in range(n_complexes):
            indices = np.arange(complex_index, population_size, n_complexes)
            complexes.append(population[indices].copy())
            complex_scores.append(scores[indices].copy())

        budget_exhausted = False
        for complex_index in range(n_complexes):
            points = complexes[complex_index]
            values = complex_scores[complex_index]

            for _ in range(evolution_steps):
                if evaluations >= max_evaluations:
                    budget_exhausted = True
                    break

                local_order = np.argsort(values)
                points = points[local_order]
                values = values[local_order]

                simplex_indices = _ranked_sample(
                    rng, complex_size, n_parameters + 1
                )
                simplex = points[simplex_indices].copy()
                simplex_scores = values[simplex_indices].copy()
                simplex_order = np.argsort(simplex_scores)
                simplex = simplex[simplex_order]
                simplex_scores = simplex_scores[simplex_order]

                centroid = simplex[:-1].mean(axis=0)
                worst = simplex[-1]
                candidate = np.clip(centroid + (centroid - worst), lower, upper)
                candidate_score = evaluate(candidate)

                if candidate_score < simplex_scores[0] and evaluations < max_evaluations:
                    expanded = np.clip(centroid + 2.0 * (candidate - centroid), lower, upper)
                    expanded_score = evaluate(expanded)
                    if expanded_score < candidate_score:
                        candidate, candidate_score = expanded, expanded_score
                elif candidate_score >= simplex_scores[-2] and evaluations < max_evaluations:
                    contracted = np.clip(worst + 0.5 * (centroid - worst), lower, upper)
                    contracted_score = evaluate(contracted)
                    if contracted_score < simplex_scores[-1]:
                        candidate, candidate_score = contracted, contracted_score
                    elif evaluations < max_evaluations:
                        candidate = rng.uniform(lower, upper)
                        candidate_score = evaluate(candidate)

                replacement_index = simplex_indices[simplex_order[-1]]
                points[replacement_index] = candidate
                values[replacement_index] = candidate_score

            complexes[complex_index] = points
            complex_scores[complex_index] = values
            if budget_exhausted:
                break

        for complex_index in range(n_complexes):
            indices = np.arange(complex_index, population_size, n_complexes)
            population[indices] = complexes[complex_index]
            scores[indices] = complex_scores[complex_index]
        shuffles += 1

        if budget_exhausted:
            break

    order = np.argsort(scores)
    population = population[order]
    scores = scores[order]
    if not history or history[-1] != float(scores[0]):
        history.append(float(scores[0]))

    return SCEUAResult(
        x=population[0].copy(),
        fun=float(scores[0]),
        n_evaluations=evaluations,
        n_shuffles=shuffles,
        converged=converged,
        history=tuple(history),
    )

