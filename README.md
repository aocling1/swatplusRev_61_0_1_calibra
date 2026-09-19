# SWAT+ Rev. 61.0.1 SCE-UA Calibration

An experimental extension of SWAT+ Revision 61.0.1 for automated parameter calibration using the Shuffled Complex Evolution–University of Arizona (SCE-UA) global optimization algorithm.

基于 SWAT+ Rev. 61.0.1 和 SCE-UA 全局优化算法的自动参数率定研究项目。

## Overview

Hydrological model calibration often requires repeatedly adjusting parameters, running simulations, and evaluating model performance. This project explores the integration of the SCE-UA global optimization algorithm with SWAT+ to automate this process.

The project is intended to help watershed and hydrology researchers:

- Reduce repetitive manual parameter adjustment.
- Search parameter spaces using SCE-UA.
- Improve the reproducibility of calibration experiments.
- Evaluate candidate parameter sets against observed data.
- Extend automated-calibration workflows for SWAT+.

## Project Status

This repository is currently an early-stage research prototype.

The source code is publicly available for research, testing, review, and further development. Documentation, reproducible examples, automated tests, and build instructions are still being improved.

It is not yet recommended for production or operational decision-making without independent validation.

## Repository Structure

```text
.
├── source_codes/                 # Existing SWAT+ / Fortran source code
├── sceua_calibration/
│   ├── sceua.py                  # Simplified SCE-UA optimizer
│   ├── example_calibration.py    # Runnable example
│   ├── swat_adapter.py           # Generic SWAT+ adapter
│   └── test_sceua.py             # Basic tests
└── README.md
```

## Quick Start for the SCE-UA Example

Python 3.10 or newer is recommended.

```bash
cd sceua_calibration
python -m pip install -r requirements.txt
python example_calibration.py
```

Run the basic tests with:

```bash
python -m unittest test_sceua.py
```

`swat_adapter.py` provides a generic interface for running an external SWAT+ executable. Project-specific functions are still required to write candidate parameters and read simulated output. The adapter is not fully connected to the existing Fortran workflow until those functions are implemented and validated.

## Requirements

Depending on the selected build environment, the following may be required:

- A compatible Fortran compiler
- SWAT+ Rev. 61.0.1 model input files
- Observed hydrological data for calibration
- Parameter definitions and valid parameter ranges
- A supported Windows or Linux development environment

## Building and Running

Detailed build and execution instructions are still being prepared.

The general workflow is:

1. Clone this repository:

   ```bash
   git clone https://github.com/aocling1/swatplusRev_61_0_1_calibra.git
   cd swatplusRev_61_0_1_calibra
   ```

2. Open the files under `source_codes/` in a compatible Fortran development environment.

3. Compile the source code using the requirements of your compiler and platform.

4. Prepare a valid SWAT+ project together with observed data, calibration parameters, parameter ranges, and an objective function.

5. Run the compiled program and inspect the generated simulation and calibration outputs.

Exact configuration files, compiler commands, and a reproducible example will be added in a future update.

## Calibration Workflow

The intended workflow is:

1. Define the SWAT+ parameters to be calibrated.
2. Specify valid lower and upper parameter bounds.
3. Generate candidate parameter sets using SCE-UA.
4. Run SWAT+ for each candidate set.
5. Compare simulated and observed values using an objective function.
6. Continue optimization until the stopping criteria are reached.
7. Export the best-performing parameter set and calibration results.

## Planned Improvements

- Complete build instructions
- Example watershed dataset
- Parameter configuration documentation
- Objective-function documentation
- Reproducible calibration example
- Regression tests
- Continuous integration
- Versioned releases

## Contributing

Issues and pull requests are welcome.

When reporting a problem, please include:

- Operating system
- Compiler and compiler version
- SWAT+ project version
- Relevant input configuration
- Error messages or logs
- Steps required to reproduce the problem

## Maintainer

Primary maintainer: [aocling1](https://github.com/aocling1)

## Upstream Project and Attribution

This repository is based on SWAT+ Rev. 61.0.1.

SWAT+ is developed by the USDA Agricultural Research Service and Texas A&M AgriLife Research, with contributions from the wider SWAT community.

- SWAT+ repository: https://github.com/swat-model/swatplus
- SWAT+ documentation: https://swatplus.gitbook.io/docs/

This repository is an independent research modification and is not an official SWAT+ distribution.

## License

This project contains or modifies SWAT+ source code. The upstream SWAT+ project is distributed under the GNU Lesser General Public License v2.1.

Before redistributing or releasing modified source code, the applicable upstream copyright notices and license terms must be preserved. See the `LICENSE` file for details.

## Disclaimer

This software is provided for research and educational purposes. Calibration results should be independently checked before being used in scientific conclusions, engineering designs, environmental management, or policy decisions.
