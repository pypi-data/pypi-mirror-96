# History

## v0.2.0 - 2021-02-24

Dependency upgrades to ensure compatibility with the rest of the SDV ecosystem.

## v0.1.3 - 2021-02-13

Updates the required dependecies to facilitate a conda release.

### Issues closed

* Upgrade sktime - Issue [#49](https://github.com/sdv-dev/SDMetrics/issues/49) by @fealho

## v0.1.2 - 2021-01-27

Big fixing release that addresses several minor errors.

### Issues closed

* More splits than classes - Issue [#46](https://github.com/sdv-dev/SDMetrics/issues/46) by @fealho
* Scipy 1.6.0 causes an AttributeError - Issue [#44](https://github.com/sdv-dev/SDMetrics/issues/44) by @fealho
* Time series metrics fails with variable length timeseries - Issue [#42](https://github.com/sdv-dev/SDMetrics/issues/42) by @fealho
* ParentChildDetection metrics KeyError - Issue [#39](https://github.com/sdv-dev/SDMetrics/issues/39) by @csala

## v0.1.1 - 2020-12-30

This version adds Time Series Detection and Efficacy metrics, as well as a fix
to ensure that Single Table binary classification efficacy metrics work well
with binary targets which are not boolean.

### Issues closed

* Timeseries efficacy metrics - Issue [#35](https://github.com/sdv-dev/SDMetrics/issues/35) by @csala
* Timeseries detection metrics - Issue [#34](https://github.com/sdv-dev/SDMetrics/issues/34) by @csala
* Ensure binary classification targets are bool - Issue [#33](https://github.com/sdv-dev/SDMetrics/issues/33) by @csala

## v0.1.0 - 2020-12-18

This release introduces a new project organization and API, with metrics
grouped by data modality, with a common API:

* Single Column
* Column Pair
* Single Table
* Multi Table
* Time Series

Within each data modality, different families of metrics have been implemented:

* Statistical
* Detection
* Bayesian Network and Gaussian Mixture Likelihood
* Machine Learning Efficacy

## v0.0.4 - 2020-11-27

Patch release to relax dependencies and avoid conflicts when using the latest SDV version.

## v0.0.3 - 2020-11-20

Fix error on detection metrics when input data contains infinity or NaN values.

### Issues closed

* ValueError: Input contains infinity or a value too large for dtype('float64') - Issue [#11](https://github.com/sdv-dev/SDMetrics/issues/11) by @csala

## v0.0.2 - 2020-08-08

Add support for Python 3.8 and a broader range of dependencies.

## v0.0.1 - 2020-06-26

First release to PyPI.
