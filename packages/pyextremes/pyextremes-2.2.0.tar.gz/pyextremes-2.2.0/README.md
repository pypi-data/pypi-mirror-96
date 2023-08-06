<p align="center" style="font-size:40px; margin:0px 10px 0px 10px">
    <em>pyextremes</em>
</p>
<p align="center">
    <em>Extreme Value Analysis (EVA) in Python</em>
</p>
<p align="center">
<a href="https://github.com/georgebv/pyextremes/actions?query=workflow%3Abuild" target="_blank">
    <img src="https://github.com/georgebv/pyextremes/workflows/build/badge.svg" alt="Test">
</a>
<a href="https://codecov.io/gh/georgebv/pyextremes" target="_blank">
    <img src="https://codecov.io/gh/georgebv/pyextremes/branch/master/graph/badge.svg" alt="Coverage">
</a>
<a href="https://pypi.org/project/pyextremes" target="_blank">
    <img src="https://badge.fury.io/py/pyextremes.svg" alt="PyPI Package">
</a>
<a href="https://anaconda.org/conda-forge/pyextremes" target="_blank">
    <img src="https://img.shields.io/conda/vn/conda-forge/pyextremes.svg" alt="Anaconda Package">
</a>
</p>

# About

**Documentation:** https://georgebv.github.io/pyextremes/

**License:** [MIT](https://opensource.org/licenses/MIT)

**E-Mail:** bocharovgeorgii@gmail.com

**pyextremes** is a Python library aimed at performing univariate and multivariate
[Extreme Value Analysis (EVA)](https://en.wikipedia.org/wiki/Extreme_value_theory).
It provides tools necessary to perform a wide range of tasks required to
perform EVA, such as:

- extraction of extreme events from time series using methods such as
Block Maxima (BM) or Peaks Over Threshold (POT)
- fitting continuous distributions, such as GEVD, GPD, or user-specified
continous distributions to the extracted extreme events
- visualization of model inputs, results, and goodness-of-fit statistics
- estimation of extreme events of given probability or return period
(e.g. 100-year event) and of corresponding confidence intervals
- tools assisting with model selection and tuning, such as selection of
block size in BM and threshold in POT

# Installation

Get latest version from PyPI:

```shell
pip install pyextremes
```

Get latest experimental build from GitHub:

```shell
pip install git+https://github.com/georgebv/pyextremes
```

Get pyextremes for the Anaconda Python distribution:

```shell
conda install -c conda-forge pyextremes
```

# Tutorials

This section will be removed in the future in favor of the official documentation
which can be found at https://georgebv.github.io/pyextremes/.

- [Basic usage](https://nbviewer.jupyter.org/github/georgebv/pyextremes-notebooks/blob/master/notebooks/EVA%20basic.ipynb)
- [Threshold selection](https://nbviewer.jupyter.org/github/georgebv/pyextremes-notebooks/blob/master/notebooks/tutorials/threshold%20selection.ipynb)

# Illustrations

<p align="center" style="font-size:20px; margin:10px 10px 0px 10px">
    <em>Model diagnostic</em>
</p>
<p align="center" style="font-size:20px; margin:10px 10px 40px 10px">
  <img src="https://raw.githubusercontent.com/georgebv/pyextremes-notebooks/master/notebooks/documentation/readme%20figures/diagnostic.png" alt="Diagnostic plot" width="600px">
</p>

<p align="center" style="font-size:20px; margin:10px 10px 0px 10px">
    <em>Extreme value extraction</em>
</p>
<p align="center" style="font-size:20px; margin:10px 10px 40px 10px">
  <img src="https://raw.githubusercontent.com/georgebv/pyextremes-notebooks/master/notebooks/documentation/readme%20figures/extremes.png" alt="Diagnostic plot" width="600px">
</p>

<p align="center" style="font-size:20px; margin:10px 10px 0px 10px">
    <em>Trace plot</em>
</p>
<p align="center" style="font-size:20px; margin:10px 10px 40px 10px">
  <img src="https://raw.githubusercontent.com/georgebv/pyextremes-notebooks/master/notebooks/documentation/readme%20figures/trace.png" alt="Diagnostic plot" width="600px">
</p>

<p align="center" style="font-size:20px; margin:10px 10px 0px 10px">
    <em>Corner plot</em>
</p>
<p align="center" style="font-size:20px; margin:10px 10px 40px 10px">
  <img src="https://raw.githubusercontent.com/georgebv/pyextremes-notebooks/master/notebooks/documentation/readme%20figures/corner.png" alt="Diagnostic plot" width="600px">
</p>
