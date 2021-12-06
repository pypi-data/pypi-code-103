# Copyright 2021 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from commonconf import override_settings


fdao_catalyst_override = override_settings(
    RESTCLIENTS_CATALYST_DAO_CLASS='Mock')
