###############################################################################
# (c) Copyright 2020 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "COPYING".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from collections import defaultdict
import sys
import os
import re
import json
import zlib

import cachetools
import tornado
from tornado.escape import json_decode, json_encode

from DIRAC import gConfig, gLogger
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations
from DIRAC.Core.Workflow.Workflow import fromXMLString as workflowFromXMLString
from DIRAC.DataManagementSystem.Client.DataManager import DataManager
from DIRAC.Resources.Storage.StorageElement import StorageElement
from DIRAC.TransformationSystem.Client.TransformationClient import TransformationClient
from LHCbDIRAC.BookkeepingSystem.Client.BKQuery import makeBKPath
from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.Core.Utilities.ProductionData import getLogPath
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient
from WebAppDIRAC.Lib.WebHandler import WebHandler, WErr, asyncGen


KNOWN_DATAPKGS = ["AnalysisProductions", "WG/CharmWGProd", "WG/CharmConfig"]
DONE_TRANSFORMATION_STATES = ["Archived", "Deleted", "Cleaned", "Completed"]
RE_PACKAGE_VERSION = re.compile(r"^v(?P<major>\d+)r(?P<minor>\d+)(?:p(?P<patch>\d+))?$")


class AnalysisProductionsHandler(WebHandler):
    AUTH_PROPS = "authenticated"

    _cache = cachetools.TTLCache(
        maxsize=10 * 1024 * 1024,  # 10 megabytes
        ttl=600,  # 10 minutes
        getsizeof=sys.getsizeof,
    )

    @classmethod
    def _getFromCache(cls, key):
        """Get a JSON response string from the lifetime based cache

        :param key: The key corresponding to this response
        :returns: The value from the cache or None
        """
        try:
            value = cls._cache[key]
        except KeyError:
            return None
        else:
            gLogger.debug("Found result in cache", str(key))
            return zlib.decompress(value).decode()

    @classmethod
    def _addToCache(cls, key, value):
        """Add a JSON response string to the cache

        The string will be stored in a compressed form to minimise memory usage.

        :param key: The key corresponding to this response
        :param value: The value corresponding to this response
        :returns: The value from the cache or None
        """
        cls._cache[key] = zlib.compress(value.encode())
        gLogger.debug("Added result to cache", "(current size = %d) %s" % (cls._cache.currsize, key))

    @asyncGen
    def web_getProduction(self):
        # Parse the request parameters

        requestIDs = self.get_argument("requestIDs", None)
        if not requestIDs:
            self.set_status(400)
            return self.finish(json_encode("Invalid value of requestIDs"))
        requestIDs = json_decode(requestIDs)
        if not requestIDs:
            return self.finish(json_encode([]))

        # Use the cache if possible
        result = self._getFromCache(frozenset(requestIDs))
        if result is not None:
            return self.finish(result)

        # Get the requested productions
        productions = getProductions({"RequestID": ",".join(map(str, requestIDs))})
        if set(requestIDs) != set(p["RequestID"] for p in productions):
            self.set_status(400)
            return self.finish(json_encode("Invalid request IDs passed"))

        # Collect all transformations in a single call (it's considerably faster)
        productionIDs = [p["RequestID"] for p in productions]
        result = TransformationClient().getTransformations({"TransformationFamily": productionIDs}, limit=1000)
        allTransformations = defaultdict(list)
        for transformation in _unwrap(result):
            productionID = int(transformation["TransformationFamily"])
            allTransformations[productionID] += [transformationToDict(transformation)]

        # Create dictionaries from each production request
        result = json_encode(
            [productionToDict(production, allTransformations[production["RequestID"]]) for production in productions]
        )

        self._addToCache(frozenset(requestIDs), result)
        return self.finish(result)

    @asyncGen
    def web_listProductions(self):
        # Use the cache if possible
        result = self._getFromCache("listProductions")
        if result is not None:
            return self.finish(result)

        # Find the production requests
        rows = []
        rows += getProductions({"RequestType": "AnalysisProduction"})
        # This search filter isn't ideal but it's the only way of efficiently
        # querying for legacy productions
        rows += getProductions({"RequestType": "WGProduction", "RequestAuthor": "cburr"})

        # Transform them into a tree
        # Structure is WG > Name > Version > List[Requests]
        productions = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for row in rows:
            package, version = findPackageNameAndVersion(row["ProDetail"])

            wg = row["RequestWG"]
            name = row["RequestName"]

            # This is to account for legacy productions from WG/CharmWGProd
            # TODO: Modify the database to remove the need for this hack?
            if package != "AnalysisProductions":
                version += " (" + package + ")"
                wg = "Unknown"
                optionsDirectories = [
                    "CHARMWGPRODROOT/productions/",
                    "CHARMWGPRODROOT/../productions/",
                    "CHARMCONFIGROOT/options/WGProductions/",
                    "CHARMCONFIGOPTS/WGProductions/",
                ]
                for s in optionsDirectories:
                    if s in row["ProDetail"]:
                        name = row["ProDetail"].split(s)[1].split("/")[0]
                        break
                else:
                    raise NotImplementedError(row.get("RequestID"))

            productions[wg][name][version].append({"id": row["RequestID"], "archived": False, "published": False})

        productions = _covertToTreeModel(productions)
        result = json_encode(productions)
        self._addToCache("listProductions", result)
        return self.finish(result)


def _covertToTreeModel(data, name="."):
    """Recursively prepare data for use with an ExtJS TreeModel"""
    node = {"name": name}

    if isinstance(data, list):
        child_data = data
        node["requestIDs"] = json_encode([c["id"] for c in child_data])
        node["leaf"] = True
    else:
        child_data = [_covertToTreeModel(v, name=k) for k, v in data.items()]
        node["children"] = sorted(child_data, key=_nodeToSortKey)

    node["archived"] = all(c["archived"] for c in child_data)
    node["published"] = any(c["published"] for c in child_data)

    return node


def _unwrap(result):
    """Unwrap an S_OK/S_ERROR response, raising if appropriate

    :param result: The response from a DIRAC RPC call
    :returns: The value returned by the RPC call
    :raises: :exc:`WebAppDIRAC.Lib.WebHandler.WErr`
    """
    if not result["OK"]:
        raise WErr.fromSERROR(result)
    return result["Value"]


def _nodeToSortKey(node):
    """Key function for use with "sorted" which understands version numbers

    :param node: The extJS node data to compure the key for
    :returns: Either a string or a tuple of integers
    """
    match = RE_PACKAGE_VERSION.match(node["name"].split(" ")[0])
    if match:
        # Return negative numbers to ensure the most recent is at the top
        return [-int(x) if x else 0 for x in match.groups()]
    else:
        return node["name"]


def getProductionStatus(production):
    """Find the analyst readable production status

    Converts a dictionary describing a production (from productionToDict) into
    a string summarising the status of the production. The allowed values are:

      * waiting: Waiting for the production to start
      * active: The transformation system is processing the data
      * replicating: Waiting for the data to be copied to CERN
      * ready: Ready for use
      * archived: This has been replaced by a newer production
      * published: This has been used for a publication

    :param production: A dictionary describing a production from productionToDict
    :returns: A string describing the production's state
    """
    if production["archived"]:
        return "archived"

    if production["published"]:
        return "published"

    if not production["transformations"]:
        return "waiting"

    transformationActive = False
    for transformation in production["transformations"]:
        if transformation["transformationStatus"] in DONE_TRANSFORMATION_STATES:
            pass
        else:
            fileCounts = transformation["fileCounts"]
            if fileCounts.get("Processed", 0) != fileCounts["Total"]:
                transformationActive = True
    if transformationActive:
        return "active"

    if production["numOutputFiles"] != production["numOutputFilesAtCERN"]:
        return "replicating"

    return "ready"


def getProductions(query):
    """Query the production management system for a list of productions

    :param query: A dictionary of query parameters to pass to getProductionRequestList
    :returns: A list which each element corresponding to a row in the database
    """
    result = ProductionRequestClient().getProductionRequestList(
        0,  # Parent
        "RequestID",  # Sortby
        "DESC",  # Sort order
        0,  # Offset
        0,  # Max results
        query,
    )
    if result["OK"]:
        return _unwrap(result)["Rows"]
    else:
        raise WErr.fromSERROR(result)


def findPackageNameAndVersion(prodDetail):
    """Find the data package and version which was used to submit this production

    :param prodDetail: The prodDetail field of the production request
    :returns: A tuple containing two strings (packageName, version)
    """
    # Use regex for now instead of handling unpickling the string
    # Look for patterns like "AnalysisProductions.v1r2p3" and "CharmWGProd.v1r5"
    # TODO: Use the JSONOrPickle function when this is in v10r1
    pattern = re.compile(r"(" + "|".join([s.split("/")[-1] for s in KNOWN_DATAPKGS]) + ")" r"\.(v\d+r\d+(?:p\d+)?)")
    submitPackage = set(pattern.findall(prodDetail))
    if len(submitPackage) != 1:
        raise NotImplementedError(prodDetail, submitPackage)
    return submitPackage.pop()


def productionToDict(production, transformations):
    """Convert the response of getProductionRequestList to a dictionary

    :param production: A row returned from getProductionRequestList
    :param transformations: A list of transformations associated with this production
    :returns: A dictionary summarising this production
    """
    productionID = production["RequestID"]

    if production["RequestType"] == "AnalysisProduction":
        _, version = findPackageNameAndVersion(production["ProDetail"])
        proDetail = json.loads(production["ProDetail"])
        productionName = proDetail["p1Name"].split("-" + version + "-")[-1].split("/")[0].strip()
    else:
        productionName = "-".join(production["RequestName"].split("-")[1:])

    lfns = []
    pfns = []
    pfnsAtCERN = []
    outputSize = 0
    outputSizeAtCERN = 0
    if transformations:
        transformationID = transformations[-1]["transformationID"]

        lfnMetadata = _unwrap(BookkeepingClient().getProductionFiles(transformationID, "ALL", "ALL"))
        # Find the LFNs which were intended as output and their size
        # Mostly needed to ignore LOG files
        expectedFileTypes = transformations[-1]["steps"][-1]["outputTypes"]
        for lfn, metadata in lfnMetadata.items():
            if metadata["FileType"] not in expectedFileTypes:
                continue
            if not metadata["GotReplica"].upper().startswith("Y"):
                continue
            lfns.append(lfn)
            outputSize += metadata["FileSize"]

        if lfns:
            replicas = _unwrap(DataManager().getReplicas(lfns, getUrl=False))["Successful"]
            # Find the replicas at CERN
            for se in gConfig.getValue("/Resources/Sites/LCG/LCG.CERN.cern/SE", []):
                seLFNs = [lfn for lfn in replicas if se in replicas[lfn]]
                if not seLFNs:
                    continue
                # Lookup the corresponding PFNs
                result = _unwrap(StorageElement(se).getURL(seLFNs, protocol="root"))
                pfnsAtCERN += list(result["Successful"].values())
                # Compute the size in bytes of the data at CERN
                outputSizeAtCERN += sum(lfnMetadata[lfn]["FileSize"] for lfn in seLFNs)

    simCondDetail = json.loads(production["SimCondDetail"])
    productionInputQuery = os.path.join(
        "/",
        simCondDetail["configName"],
        simCondDetail["configVersion"],
        production["SimCondition"],
        simCondDetail["inProPass"],
        production["EventType"],
        simCondDetail["inFileType"],
    )

    outputPattern = ""
    if pfnsAtCERN:
        # Get the file extension
        extensions = set(os.path.splitext(p)[1] for p in pfnsAtCERN)
        if len(extensions) > 1:
            raise NotImplementedError(extensions)
        suffix = "*" + extensions.pop()

        # Find a common directory
        pfnDirectories = set(os.path.dirname(p) for p in pfnsAtCERN)
        if len(pfnDirectories) > 1:
            pfnDirectories = set(os.path.dirname(p) for p in pfnsAtCERN)
            if len(pfnDirectories) > 1:
                # This only goes two levels deep by convention
                raise NotImplementedError(pfnDirectories)
            suffix = "*/" + suffix
        outputPattern = pfnDirectories.pop() + "/" + suffix

    result = {
        "requestID": productionID,
        "status": production["RequestState"],
        "name": productionName,
        "outputPattern": outputPattern,
        "LFNs": lfns,
        "PFNs": pfnsAtCERN,
        "outputSize": outputSize,
        "numOutputFiles": len(lfns),
        "numOutputFilesAtCERN": len(pfnsAtCERN),
        "productionInputQuery": productionInputQuery,
        "transformations": transformations,
        "archived": False,  # TODO
        "published": False,  # TODO
    }
    result["state"] = getProductionStatus(result)
    return result


def transformationToDict(transformation):
    """Convert the response of getTransformations to a dictionary

    :param production: A row returned from getTransformations
    :returns: A dictionary summarising this transformation
    """
    transformationID = transformation["TransformationID"]
    transformationStatus = transformation["Status"]

    workflow = workflowFromXMLString(transformation["Body"])
    parameters = {p.getName(): p.getValue() for p in workflow.parameters}

    # Skip this if the transfromation is done as it's relatively slow
    fileCounts = {}
    if transformationStatus not in DONE_TRANSFORMATION_STATES:
        fileCounts = _unwrap(TransformationClient().getTransformationFilesCount(transformationID, "Status"))

    logsURL = getTransformationLogsURL(parameters["configName"], parameters["configVersion"], transformationID)

    steps = [
        stepToDict(parameters["BKProcessingPass"]["Step" + str(i)]) for i in range(len(parameters["BKProcessingPass"]))
    ]

    transformInputQuery = _unwrap(TransformationClient().getBookkeepingQuery(transformationID))

    return {
        "transformationID": transformationID,
        "transformationStatus": transformation["Status"],
        "transformationType": transformation["Type"],
        "fileCounts": fileCounts,
        "logsURL": logsURL,
        "steps": steps,
        "transformInputQuery": transformInputQuery,
    }


def stepToDict(stepData):
    """Convert a BKProcessingPass step to a dictionary

    :param production: A step from the BKProcessingPass parameter of a workflow
    :returns: A dictionary summarising this step
    """
    extras = stepData["ExtraPackages"].split(";")
    for extra in extras:
        if any(extra.startswith(package) for package in KNOWN_DATAPKGS):
            package, version = extra.split(".")
            if not RE_PACKAGE_VERSION.match(version):
                raise NotImplementedError(package, version)
            gitlabURL = "https://gitlab.cern.ch/lhcb-datapkg/" + package + "/-/tree/" + version
            break
    else:
        gitlabURL = None

    outputTypes = [d["FileType"] for d in stepData["OutputFileTypes"]]

    return {
        "stepID": stepData["BKStepID"],
        "application": stepData["ApplicationName"] + "/" + stepData["ApplicationVersion"],
        "extras": extras,
        "GitLabURL": gitlabURL,
        "options": stepData["OptionFiles"].split(";"),
        "outputTypes": outputTypes,
    }


def getTransformationLogsURL(configName, configVersion, transformationID):
    """Get the HTTPS URL on logSE for a given transformation

    :param configName: The transformations config name
    :param configVersion: The transformations config version
    :param transformationID: The ID of the transformation
    :returns: A string corresponding to the base URL of the logs
    """
    from LHCbDIRAC.Core.Utilities.ProductionData import _makeProductionPath, _getLFNRoot

    lfnRoot = _getLFNRoot("", configName, configVersion)
    lfn = _makeProductionPath("", lfnRoot, "LOG", str(transformationID).zfill(8))
    logSE = Operations().getValue("LogStorage/LogSE", "LogSE")
    result = StorageElement(logSE).getURL(lfn, protocol="https")
    return _unwrap(result)["Successful"][lfn]
