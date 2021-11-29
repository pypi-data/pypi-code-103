# -*- coding: utf-8 -*-
"""
Initializes this package with metadata.
"""

from .metadata import (
        __version__,
        __author__,
        __copyright__,
        __credits__,
        __license__,
        __maintainer__,
        __email__,
        __status__,
    )

from .main import (
        get_next_generation_matrix_from_matrices,
        get_contribution_matrix,
        get_2d_contribution_matrix,
        get_reduced_contribution_matrix,
        get_reduced_vaccinated_susceptible_contribution_matrix,
        get_reduced_population_contribution_matrix,
        get_homogeneous_contribution_matrix,
        get_homogeneous_next_generation_matrix,
        get_eigenvector,
        get_homogeneous_eigenvector,
        get_reduced_vaccinated_susceptible_eigenvector,
        get_reduced_population_eigenvector,
    )

from .covid import (
        get_covid_matrices,
        get_next_generation_matrix_covid,
        get_contribution_matrix_covid,
        get_reduced_contribution_matrix_covid,
        get_reduced_vaccinated_susceptible_contribution_matrix_covid,
        get_reduced_population_contribution_matrix_covid,
    )

from .linalg import (
        get_spectral_radius_and_eigenvector,
        convert_4d_matrix_to_2d_block,
    )
