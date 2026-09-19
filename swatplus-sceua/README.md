# SWAT+ Rev. 61.0.1 SCE-UA Calibration

An early-stage research project for automated SWAT+ parameter calibration using the Shuffled Complex Evolution–University of Arizona (SCE-UA) global optimization algorithm.

基于 SWAT+ Rev. 61.0.1 和 SCE-UA 全局优化算法的自动参数率定研究项目。

## Overview

Hydrological calibration requires repeated parameter updates, simulations, and comparisons with observed data. This repository provides a compact SCE-UA reference implementation and a generic adapter for connecting the optimizer to an external SWAT+ executable.

The project aims to:

- Reduce repetitive manual parameter adjustment.
- Search bounded parameter spaces with SCE-UA.
- Improve the reproducibility of calibration experiments.
- Provide a clear starting point for SWAT+ calibration automation.

## Project Status

This repository is an early-stage research prototype. The included SCE-UA implementation is intentionally compact and should be independently validated before it is used for scientific conclusions or operational decisions.

## Repository Structure

```text
.
├── source_codes/                 # Existing SWAT+ / Fortran source code
├── sceua_calibration/
│   ├── __init__.py
│   ├── sceua.py                  # Simplified SCE-UA optimizer
│   ├── example_calibration.py    # Runnable synthetic example
│   ├── swat_adapter.py           # Generic external SWAT+ adapter
│   ├── test_sceua.py             # Basic unit tests
│   └── requirements.txt
└── README.md
```

## Quick Start

Python 3.10 or newer is recommended.

```bash
git clone https://github.com/aocling1/swatplusRev_61_0_1_calibra.git
cd swatplusRev_61_0_1_calibra/sceua_calibration
python -m pip install -r requirements.txt
python example_calibration.py
```

Run the basic tests with:

```bash
python -m unittest test_sceua.py
```

## Minimal Usage

```python
import numpy as np

from sceua import sceua


def objective(parameters: np.ndarray) -> float:
    target = np.array([0.25, -0.40])
    return float(np.sum((parameters - target) ** 2))


result = sceua(
    objective,
    bounds=[(-2.0, 2.0), (-2.0, 2.0)],
    max_evaluations=1200,
    seed=42,
)

print(result.x)
print(result.fun)
```

The optimizer minimizes the objective function. For hydrological calibration, the objective may be RMSE, negative Nash–Sutcliffe efficiency, or another carefully selected statistic.

## Connecting to SWAT+

`swat_adapter.py` contains a generic `SWATObjective` class. Each evaluation:

1. Copies a clean SWAT+ project template into a temporary workspace.
2. Calls a project-specific function to write candidate parameters.
3. Runs the configured SWAT+ executable without invoking a shell.
4. Calls a project-specific function to read simulated values.
5. Returns the RMSE between simulated and observed series.

Because SWAT+ project layouts and calibration files differ, you must implement two callbacks:

- `parameter_writer(workspace, parameters)`
- `output_reader(workspace)`

The adapter should not be considered fully connected to this repository's existing Fortran workflow until those functions have been implemented and validated against a known watershed case.

## SCE-UA Workflow

The simplified implementation follows this general process:

1. Sample an initial population inside the parameter bounds.
2. Rank candidates by their objective values.
3. Partition the population into complexes.
4. Evolve each complex using ranked simplex selection, reflection, expansion, contraction, and random replacement.
5. Shuffle the complexes and repeat until the evaluation budget or convergence criterion is reached.

## Planned Improvements

- Project-specific SWAT+ parameter writer
- SWAT+ output parser
- Reproducible watershed example
- Additional objective functions and evaluation metrics
- Regression tests against published SCE-UA benchmarks
- Continuous integration and versioned releases

## Contributing

Issues and pull requests are welcome. Please include your operating system, Python or Fortran compiler version, SWAT+ version, relevant configuration, and reproducible error details.

## Maintainer

Primary maintainer: [aocling1](https://github.com/aocling1)

## Upstream Project and Attribution

This repository is based on SWAT+ Rev. 61.0.1. SWAT+ is developed by the USDA Agricultural Research Service and Texas A&M AgriLife Research, with contributions from the wider SWAT community.

- SWAT+ repository: https://github.com/swat-model/swatplus
- SWAT+ documentation: https://swatplus.gitbook.io/docs/

This repository is an independent research modification and is not an official SWAT+ distribution.

## License

This project contains or modifies SWAT+ source code. The upstream SWAT+ project is distributed under the GNU Lesser General Public License v2.1. Preserve all applicable upstream copyright notices and license terms, and include the complete license text in a root-level `LICENSE` file before redistribution.

## Disclaimer

This software is provided for research and educational purposes without warranty. Calibration results must be independently validated before use in scientific, engineering, environmental-management, or policy decisions.

