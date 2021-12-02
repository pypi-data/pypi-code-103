"""A general class for holding solutions to pathway analyses."""
# The MIT License (MIT)
#
# Copyright (c) 2013 Weizmann Institute of Science
# Copyright (c) 2018-2020 Institute for Molecular Systems Biology,
# ETH Zurich
# Copyright (c) 2018-2020 Novo Nordisk Foundation Center for Biosustainability,
# Technical University of Denmark
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from equilibrator_api import R, default_T, standard_concentration
from sbtab import SBtab

from .pathway import Pathway


class PathwayAnalysisSolution(object):
    """A general class for pathway analysis results."""

    def __init__(
        self,
        pathway: Pathway,
        score: float,
        ln_conc: np.ndarray,
        y: Optional[np.array] = None,
    ) -> None:
        """

        Parameters
        ----------
        thermo_model : ThermodynamicModel
        ln_conc : array
            log concentrations at MDF optimum
        """
        self.score = score
        self.ln_conc = ln_conc
        self.ln_conc_mu = pathway.ln_conc_mu
        self.ln_conc_sigma = pathway.ln_conc_sigma
        self.dg_confidence = pathway.dg_confidence
        self.ln_conc_confidence = pathway.ln_conc_confidence
        self.y = y

        standard_dg_primes = pathway.standard_dg_primes.squeeze()

        physiological_dg_primes = standard_dg_primes.copy()
        for i, rxn in enumerate(pathway.reactions):
            physiological_dg_primes[i] += (
                rxn.physiological_dg_correction() * R * default_T
            )

        optimized_dg_primes = standard_dg_primes.copy()
        _dg_adj = (pathway.S.T @ self.ln_conc).values.squeeze()
        optimized_dg_primes += _dg_adj * R * default_T

        # add the calculated error values (due to the ΔG'0 uncertainty)
        if y is not None and pathway.dg_sigma is not None:
            dg_adjustment = pathway.dg_sigma @ y.squeeze()
        else:
            dg_adjustment = np.zeros(standard_dg_primes.shape)

        # adjust ΔGs to flux directions
        standard_dg_primes = pathway.I_dir @ standard_dg_primes
        physiological_dg_primes = pathway.I_dir @ physiological_dg_primes
        optimized_dg_primes = pathway.I_dir @ optimized_dg_primes
        dg_adjustment = pathway.I_dir @ dg_adjustment

        # all dG values are in units of RT, so we convert them to kJ/mol
        reaction_data = zip(
            pathway.reaction_ids,
            pathway.reaction_formulas,
            pathway.fluxes,
            standard_dg_primes,
            standard_dg_primes + dg_adjustment,
            physiological_dg_primes + dg_adjustment,
            optimized_dg_primes + dg_adjustment,
        )
        self._reaction_df = pd.DataFrame(
            data=list(reaction_data),
            columns=[
                "reaction_id",
                "reaction_formula",
                "flux",
                "original_standard_dg_prime",
                "standard_dg_prime",
                "physiological_dg_prime",
                "optimized_dg_prime",
            ],
        )

        lbs, ubs = pathway.bounds
        compound_data = zip(
            pathway.compound_ids,
            np.exp(self.ln_conc).flatten() * standard_concentration,
            lbs,
            ubs,
        )
        self._compound_df = pd.DataFrame(
            data=list(compound_data),
            columns=[
                "compound_id",
                "concentration",
                "lower_bound",
                "upper_bound",
            ],
        )

    @property
    def reaction_df(self) -> pd.DataFrame:
        """Get a DataFrame with all the reaction data.

        The columns are:
            reaction_id
            reaction_formula
            flux
            original_standard_dg_prime
            standard_dg_prime
            physiological_dg_prime
            optimized_dg_prime

        """
        return self._reaction_df

    @property
    def compound_df(self) -> pd.DataFrame:
        """Get a DataFrame with all the compound data.

        The columns are:
            compound_id
            concentration
            lower_bound
            upper_bound

        """
        return self._compound_df

    @property
    def reaction_ids(self) -> Iterable[str]:
        return self._reaction_df.reaction_id.__iter__()

    @property
    def compound_ids(self) -> Iterable[str]:
        return self._compound_df.compound_id.__iter__()

    def to_sbtab(self) -> SBtab.SBtabDocument:
        """Generate a report (in SBtab format)."""
        sbtabdoc = SBtab.SBtabDocument("report")

        # add a table with the optimized metabolite concentrations
        met_data = []
        for row in self.compound_df.itertuples():
            met_data.append(
                (
                    "concentration",
                    row.compound_id,
                    f"{row.concentration.m_as('M'):.3e}",
                )
            )
        met_df = pd.DataFrame(
            columns=["!QuantityType", "!Compound", "!Value"], data=met_data
        )
        met_sbtab = SBtab.SBtabTable.from_data_frame(
            met_df,
            table_id="Predicted concentrations",
            table_type="Quantity",
            unit="M",
        )
        sbtabdoc.add_sbtab(met_sbtab)

        # add a table with the optimized reaction Gibbs energies
        rxn_data = []
        for row in self.reaction_df.itertuples():
            rxn_data.append(
                (
                    "reaction gibbs energy",
                    row.reaction_id,
                    f"{row.optimized_dg_prime.m_as('kJ/mol'):.3e}",
                )
            )
        rxn_df = pd.DataFrame(
            columns=["!QuantityType", "!Reaction", "!Value"], data=rxn_data
        )
        rxn_sbtab = SBtab.SBtabTable.from_data_frame(
            rxn_df,
            table_id="Predicted Gibbs energies",
            table_type="Quantity",
            unit="kJ/mol",
        )
        sbtabdoc.add_sbtab(rxn_sbtab)

        return sbtabdoc
