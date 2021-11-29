###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""
    This module implements the default behavior for the FTS3Agent for TPC and source SE selection
"""
import random
import itertools
from DIRAC import S_OK, S_ERROR
from DIRAC.DataManagementSystem.Utilities.DMSHelpers import DMSHelpers
from DIRAC.DataManagementSystem.private.FTS3Plugins.DefaultFTS3Plugin import DefaultFTS3Plugin
from DIRAC.Resources.Storage.StorageElement import StorageElement


class LHCbFTS3Plugin(DefaultFTS3Plugin):
    @staticmethod
    def _isCERNEOSCTATransfer(ftsJob=None, sourceSEName=None, destSEName=None, **kwargs):
        """Check if the transfer involves both CERN EOS and CTA"""
        try:
            if not sourceSEName:
                sourceSEName = ftsJob.sourceSE
            if not destSEName:
                destSEName = ftsJob.targetSE

            srcSE = StorageElement(sourceSEName)
            srcBaseSEName = srcSE.options.get("BaseSE")
            dstSE = StorageElement(destSEName)
            dstBaseSEName = dstSE.options.get("BaseSE")

            if (srcBaseSEName, dstBaseSEName) in list(itertools.product(("CERN-EOS", "CERN-CTA"), repeat=2)):
                return True

        except Exception:
            pass

        return False

    def selectTPCProtocols(self, ftsJob=None, sourceSEName=None, destSEName=None, **kwargs):
        """Specialised TPC selection"""

        # If the transfer involves both CERN EOS and CTA, return root as TPC
        if self._isCERNEOSCTATransfer(ftsJob=ftsJob, sourceSEName=sourceSEName, destSEName=destSEName, **kwargs):
            return ["root"]

        return super(LHCbFTS3Plugin, self).selectTPCProtocols(
            ftsJob=ftsJob, sourceSEName=sourceSEName, destSEName=destSEName, **kwargs
        )

    # According to RAL, their problem is fixed,
    # (https://ggus.eu/?mode=ticket_info&ticket_id=151955#update#13
    # so I comment this out, but I'll keep it a bit
    # for ease of hotfixing, you know, just in case...

    # def selectSourceSE(self, ftsFile, replicaDict, allowedSources):
    #   """
    #     This is basically a copy/paste of the parent method, with the exception
    #     of not staging between CTA and Echo....
    #   """

    #   allowedSourcesSet = set(allowedSources) if allowedSources else set()
    #   # Only consider the allowed sources

    #   # If we have a restriction, apply it, otherwise take all the replicas
    #   allowedReplicaSource = (set(replicaDict) & allowedSourcesSet) if allowedSourcesSet else replicaDict

    #   # If we have CTA and RAL as a tape source, choose RAL.
    #   if 'CERN-RAW' in allowedReplicaSource and 'RAL-RAW' in allowedReplicaSource:
    #     allowedReplicaSource = {'RAL-RAW': True}
    #   # pick a random source

    #   randSource = random.choice(list(allowedReplicaSource))  # one has to convert to list
    #   return randSource

    def inferFTSActivity(self, ftsOperation, rmsRequest, rmsOperation):
        """
        Tries to infer the FTS Activity
        """

        ### Data Challenge activity
        # All the tests with data challenges are done
        # on SE with '-DC-' in their name
        targetSEs = rmsOperation.targetSEList
        if any("-DC-" in se for se in targetSEs):
            return "Data Challenge"

        return super(LHCbFTS3Plugin, self).inferFTSActivity(ftsOperation, rmsRequest, rmsOperation)
