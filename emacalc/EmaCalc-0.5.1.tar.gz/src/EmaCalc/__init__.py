"""This package implements a Bayesian probabilistic model for
analysis of Ecological Momentary Assessment (EMA) data.

EMA methodology is used, for example,
to evaluate the subjective performance of hearing aids or other equipment,
or the effect of any other kind of psycho-social intervention,
in the everyday life of the user or client.

For example, in an EMA study of Common Sound Scenarios of hearing-aid users,
the participants might be asked to report, at random occasions in their daily life,
which type of activity they are currently engaged in,
or in which type of sound environment they are currently using their hearing aids,
and (perhaps) how important the current situation is.

The participants may also be asked to grade the performance of their current hearing aids,
for one or more perceptual Attributes, e.g., Speech Understanding and/or Sound Pleasantness.

Thus, EMA data usually include both NOMINAL and ORDINAL results.
Typically, many EMA records are collected from each participant,
but the number of records may vary a lot among respondents.

*** Main Modules:
ema_data: defines classes EmaFrame, EmaDataSet, and input functions for EMA data

ema_model: defines class EmaModel as a probabilistic model for EMA data
    and a variational learning algorithm for all model parameters

ema_display: classes and functions to display analysis results

ema_base: defines class PopulationMixtureBase for mixture components,
    and internal functions and properties for the storage format of model parameters.

*** Reference:
A Leijon (2021): Bayesian Analysis of Ecological Momentary Assessment (EMA) Data.
Tech Report.

*** Version History:
* Version 0.5.1: Minor update:
2021-11-25, allow EMA study with NO Attributes, i.e., ONLY Scenario probability profile(s)
2021-12-02, Minor fix: Attribute location == 0 given FIRST Scenario category
            regardless of regression_effect specification.

* Version 0.5:
2021-10-12, Crude version, based on CountProfileCalc-2021, and PairedCompCalc (on PyPi),
2021-11-24, Functional beta version tested with simulated and (some) real data.
"""
__name__ = 'EmaCalc'
__version__ = '0.5.1'

__all__ = ['__version__', 'run_ema', 'run_sim']
