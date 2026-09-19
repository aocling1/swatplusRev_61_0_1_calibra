"""Generic adapter for connecting SCE-UA to an external SWAT+ executable.

Project-specific parameter and output formats differ. Supply callbacks that
write a parameter vector into a copied SWAT+ project and read its simulation
output. The adapter deliberately avoids shell execution.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Callable, Sequence

import numpy as np


ParameterWriter = Callable[[Path, np.ndarray], None]
OutputReader = Callable[[Path], Sequence[float] | np.ndarray]


class SWATObjective:
    """Callable RMSE objective that runs a fresh SWAT+ workspace each time."""

    def __init__(
        self,
        template_directory: str | Path,
        executable: str | Path,
        observed: Sequence[float] | np.ndarray,
        parameter_writer: ParameterWriter,
        output_reader: OutputReader,
        *,
        timeout_seconds: float = 600.0,
    ) -> None:
        self.template_directory = Path(template_directory).resolve()
        self.executable = Path(executable).resolve()
        self.observed = np.asarray(observed, dtype=float)
        self.parameter_writer = parameter_writer
        self.output_reader = output_reader
        self.timeout_seconds = timeout_seconds

        if not self.template_directory.is_dir():
            raise ValueError("template_directory must be an existing directory")
        if not self.executable.is_file():
            raise ValueError("executable must be an existing file")
        if self.observed.ndim != 1 or self.observed.size == 0:
            raise ValueError("observed must be a non-empty one-dimensional series")

    def __call__(self, parameters: np.ndarray) -> float:
        with tempfile.TemporaryDirectory(prefix="swat_sceua_") as temporary:
            workspace = Path(temporary) / "project"
            shutil.copytree(self.template_directory, workspace)
            self.parameter_writer(workspace, parameters.copy())

            completed = subprocess.run(
                [str(self.executable)],
                cwd=workspace,
                check=False,
                timeout=self.timeout_seconds,
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                return float("inf")

            simulated = np.asarray(self.output_reader(workspace), dtype=float)
            if simulated.shape != self.observed.shape or not np.all(np.isfinite(simulated)):
                return float("inf")
            return float(np.sqrt(np.mean((simulated - self.observed) ** 2)))

