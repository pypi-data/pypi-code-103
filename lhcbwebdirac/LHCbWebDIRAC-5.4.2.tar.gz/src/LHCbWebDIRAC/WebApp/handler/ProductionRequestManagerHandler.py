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
""" Web Handler for ProductionRequest service
"""
import json
import datetime
import tornado
from six import text_type
import six

from WebAppDIRAC.Lib.WebHandler import WebHandler, WErr, asyncGen

from DIRAC import S_ERROR, S_OK, gConfig, gLogger
from DIRAC.ConfigurationSystem.Client import PathFinder
from DIRAC.Core.Utilities import DictCache
from DIRAC.Core.Utilities import Time

from LHCbDIRAC.BookkeepingSystem.Client.BookkeepingClient import BookkeepingClient
from LHCbDIRAC.ProductionManagementSystem.Client.ProductionRequestClient import ProductionRequestClient
from LHCbWebDIRAC.WebApp.handler.ProductionLib import SelectAndSort, PrTpl
from LHCbDIRAC.BookkeepingSystem.Client.LHCB_BKKDBClient import LHCB_BKKDBClient


class ProductionRequestManagerHandler(WebHandler):

    AUTH_PROPS = "authenticated"

    __dataCache = DictCache.DictCache()

    serviceFields = [
        "RequestID",
        "HasSubrequest",
        "ParentID",
        "MasterID",
        "RequestName",
        "RequestType",
        "RequestState",
        "RequestPriority",
        "RequestAuthor",
        "RequestPDG",
        "RequestWG",
        "SimCondition",
        "SimCondID",
        "ProPath",
        "ProID",
        "EventType",
        "NumberOfEvents",
        "Comments",
        "Description",
        "Inform",
        "IsModel",
        "StartingDate",
        "FinalizationDate",
        "FastSimulationType",
        "RetentionRate",
        "bk",
        "bkTotal",
        "rqTotal",
        "crTime",
        "upTime",
    ]
    localFields = [
        "ID",
        "_is_leaf",
        "_parent",
        "_master",
        "reqName",
        "reqType",
        "reqState",
        "reqPrio",
        "reqAuthor",
        "reqPDG",
        "reqWG",
        "simDesc",
        "simCondID",
        "pDsc",
        "pID",
        "eventType",
        "eventNumber",
        "reqComment",
        "reqDesc",
        "reqInform",
        "IsModel",
        "StartingDate",
        "FinalizationDate",
        "FastSimulationType",
        "RetentionRate",
        "eventBK",
        "eventBKTotal",
        "EventNumberTotal",
        "creationTime",
        "lastUpdateTime",
    ]

    simcondFields = [
        "Generator",
        "MagneticField",
        "BeamEnergy",
        "Luminosity",
        "DetectorCond",
        "BeamCond",
        "configName",
        "configVersion",
        "condType",
        "inProPass",
        "inFileType",
        "inProductionID",
        "inDataQualityFlag",
        "G4settings",
        "inTCKs",
    ]

    proStepFields = [
        "Step",
        "Name",
        "Pass",
        "App",
        "Ver",
        "Opt",
        "OptF",
        "DDDb",
        "CDb",
        "DQT",
        "EP",
        "Vis",
        "Use",
        "IFT",
        "OFT",
        "Html",
    ]

    extraFields = ["mcConfigVersion"]

    bkSimCondFields = [
        "simCondID",
        "simDesc",
        "BeamCond",
        "BeamEnergy",
        "Generator",
        "MagneticField",
        "DetectorCond",
        "Luminosity",
        "G4settings",
    ]

    def __unescape(self, d):
        """Unescape HTML code in parameters"""
        for x in d:
            d[x] = text_type(d[x][-1])
            s = d[x].replace("&amp;", "&")
            while s != d[x]:
                d[x] = s
                s = d[x].replace("&amp;", "&")
            d[x] = d[x].replace("&lt;", "<")
            d[x] = d[x].replace("&gt;", ">")

    def __fromlocal(self, req):
        result = {}
        for x, y in zip(self.localFields[2:-5], self.serviceFields[2:-5]):
            if x == "eventType" and "eventType" in req:
                result[y] = req[x]
            elif x in req and req[x]:
                result[y] = req[x]

        SimCondDetail = {}
        for x in self.simcondFields:
            if x in req and str(req[x]) != "":
                SimCondDetail[x] = req[x]
        if SimCondDetail:
            result["SimCondDetail"] = json.dumps(SimCondDetail)

        ProDetail = {}
        for x in req:
            if str(x)[0] == "p" and str(x) != "progress":
                if str(req[x]) != "":
                    ProDetail[x] = req[x]
        if ProDetail:
            result["ProDetail"] = json.dumps(ProDetail)

        Extra = {}
        for x in self.extraFields:
            if x in req and str(req[x]) != "":
                Extra[x] = req[x]
        if Extra:
            result["Extra"] = json.dumps(Extra)

        return result

    def __request_types(self):
        types = ""
        csS = PathFinder.getServiceSection("ProductionManagement/ProductionRequest")
        if csS:
            types = gConfig.getValue("%s/RequestTypes" % csS, "")
        if not types:
            return ["Simulation", "Reconstruction", "Stripping"]
        return types.split(", ")

    def __getArgument(self, argName, argDefValue):
        return self.get_argument(argName, None) or argDefValue

    def __getJsonArgument(self, argName, argDefValue):
        x = self.get_argument(argName, None)
        return json.loads(x) if x else argDefValue

    @staticmethod
    def __bkProductionProgress(prId):
        result = BookkeepingClient().getProductionInformations(prId)
        if not result["OK"]:
            return result
        info = result["Value"]
        if "Number of events" not in info:
            return S_OK(0)
        allevents = info["Number of events"]
        if not allevents:
            return S_OK(0)
        if len(allevents) > 1:
            return S_ERROR("More than one output file type. Unsupported.")
        return S_OK(allevents[0][1])

    def __2local(self, req):
        result = {}

        for x, y in zip(self.localFields, self.serviceFields):
            if isinstance(req[y], (datetime.date, datetime.datetime)):
                result[x] = str(req[y])
            else:
                result[x] = req[y]
        result["_is_leaf"] = not result["_is_leaf"]
        if req["bkTotal"] is not None and req["rqTotal"] is not None and req["rqTotal"]:
            result["progress"] = int(req["bkTotal"]) * 100 / int(req["rqTotal"])
        else:
            result["progress"] = None
        if req["SimCondDetail"]:
            try:
                result.update(json.loads(req["SimCondDetail"]))
            except Exception:
                gLogger.error("Bad requests: simulation/data taking conditions is not defined", req["RequestID"])

        if req["ProDetail"]:
            try:
                result.update(json.loads(req["ProDetail"]))
            except Exception:
                gLogger.error("Bad requests: processing pass is not defined", req["RequestID"])

        if req["Extra"]:
            result.update(json.loads(req["Extra"]))
        for x, value in result.items():
            if x != "_parent" and value is None:
                result[x] = ""
        return result

    def __parseRequest(self):
        path = self.get_argument("fullpath", "")
        rType = self.get_argument("type", "") == "adv"
        tree = self.get_argument("tree", "Configuration")

        dataQuality = None
        if "dataQuality" in self.request.arguments:
            dataQuality = dict(json.loads(self.get_argument("dataQuality")))
            if not dataQuality:
                dataQuality = {"OK": True}

        self.numberOfJobs = int(self.get_argument("limit", "25"))
        self.pageNumber = int(self.get_argument("start", "0"))
        return path, rType, tree, dataQuality

    def __condFromPath(self, path, bkcli, item):
        runCondTr = {
            "DaqperiodId": "simCondID",
            "Description": "simDesc",
            "BeamCondition": "BeamCond",
            "BeanEnergy": "BeamEnergy",
            "MagneticField": "MagneticField",
            "VELO": "detVELO",
            "IT": "detIT",
            "TT": "detTT",
            "OT": "detOT",
            "RICH1": "detRICH1",
            "RICH2": "detRICH2",
            "SPD_PRS": "detSPD_PRS",
            "ECAL": "detECAL",
            "HCAL": "detHCAL",
            "MUON": "detMUON",
            "L0": "detL0",
            "HLT": "detHLT",
            "VeloPosition": "VeloPosition",
        }
        simCondTr = {
            "BeamEnergy": "BeamEnergy",
            "Description": "simDesc",
            "Generator": "Generator",
            "Luminosity": "Luminosity",
            "G4settings": "G4settings",
            "MagneticField": "MagneticField",
            "DetectorCondition": "DetectorCond",
            "BeamCondition": "BeamCond",
            "SimId": "simCondID",
        }

        p = path.split("/")
        condp = "/".join(p[0:4])
        if not item:
            dirp = "/".join(p[0:3])
            allcond = bkcli.list(dirp)
            cond = {}
            for x in allcond:
                if x["fullpath"] == condp:
                    cond = x
                    break
            if not cond:
                return S_ERROR("Could not find %s" % condp)
        else:
            cond = item
        if cond["level"] != "Simulation Conditions/DataTaking":
            return S_ERROR("%s is not a condition" % condp)
        for x in ["level", "expandable", "name", "fullpath", "selection", "method"]:
            if x in cond:
                del cond[x]
        if "DaqperiodId" in cond:
            tr, rType = runCondTr, "Run"
        else:
            tr, rType = simCondTr, "Simulation"
        nm = [x for x in cond if x not in tr]
        if nm:
            return S_ERROR("Unmached run conditions: %s" % str(nm))
        v = dict([(tr[x], cond[x]) for x in cond])
        v["condType"] = rType
        if rType == "Run":
            v["DetectorCond"] = self.__runDetectorCond(v)
        return S_OK(v)

    def __runDetectorCond(self, cond):
        subd = [
            "detVELO",
            "detIT",
            "detTT",
            "detOT",
            "detRICH1",
            "detRICH2",
            "detSPD_PRS",
            "detECAL",
            "detHCAL",
            "detMUON",
            "detL0",
            "detHLT",
        ]
        incl = []
        not_incl = []
        unknown = []
        for x in subd:
            if x not in cond:
                unknown.append(x[3:])
            elif cond[x] == "INCLUDED":
                incl.append(x[3:])
            elif cond[x] == "NOT INCLUDED":
                not_incl.append(x[3:])
            else:
                unknown.append(x[3:])
        if len(incl) > len(not_incl):
            if not not_incl:
                s = "all"
                if unknown:
                    s += " except unknown %s" % ",".join(unknown)
            else:
                s = "without %s" % ",".join(not_incl)
                if unknown:
                    s += " and unknown %s" % ",".join(unknown)
        else:
            if incl:
                s = "only %s" % ",".join(incl)
                if unknown:
                    s += " and unknown %s" % ",".join(unknown)
            else:
                s = "no"
                if unknown:
                    s += " with unknown %s" % ",".join(unknown)
        return s

    @asyncGen
    def web_getSelectionData(self):
        callback = {}
        retVal = yield self.threadTask(ProductionRequestClient().getFilterOptions)
        if not retVal["OK"]:
            self.finish({"success": "false", "result": [], "total": 0, "error": retVal["Message"]})
            return

        callback["typeF"] = [[i] for i in retVal["Value"]["Type"]]
        callback["stateF"] = [[i] for i in retVal["Value"]["State"]]
        callback["authorF"] = [[i] for i in retVal["Value"]["Author"]]
        callback["wgF"] = [[i] for i in retVal["Value"]["WG"]]

        self.write(callback)

    @asyncGen
    def web_getWG(self):
        retVal = yield self.threadTask(ProductionRequestClient().getFilterOptions)
        if not retVal["OK"]:
            raise WErr.fromSERROR(retVal)
        rows = [{"text": i, "name": i} for i in retVal["Value"]["WG"]]
        self.finish({"OK": True, "result": rows, "total": len(rows)})

    @asyncGen
    def web_list(self):
        parent = self.get_argument("anode", 0)
        try:
            if parent != 0:
                parent = json.loads(parent)
                if isinstance(parent, list):
                    parent = parent[-1]
        except Exception as e:
            raise WErr(404, e)

        result = yield self.threadTask(self.getProductionRequestList, parent)
        self.finish(result)

    @asyncGen
    def web_history(self):
        requestID = self.get_argument("RequestID", "")
        try:
            requestID = int(json.loads(requestID))
        except Exception:
            self.finish({"success": "false", "result": [], "total": 0, "error": "Request ID is not a number"})

        result = yield self.threadTask(ProductionRequestClient().getRequestHistory, requestID)
        if not result["OK"]:
            self.finish({"success": "false", "result": [], "total": 0, "error": result["Message"]})
            return
        rows = result["Value"]["Rows"]
        result = []
        for row in rows:
            row["TimeStamp"] = str(row["TimeStamp"])
            result += [[row["TimeStamp"], row["RequestState"], row["RequestUser"]]]
        self.finish({"success": "true", "result": result, "total": len(result)})

    @asyncGen
    def web_duplicate(self):
        try:
            reqId = self.get_argument("ID")
            clearpp = self.get_argument("ClearPP")
            reqId = int(json.loads(reqId))
            clearpp = json.loads(clearpp)
        except Exception:
            self.finish({"success": "false", "result": [], "total": 0, "error": "Request ID is not a number"})

        result = yield self.threadTask(ProductionRequestClient().duplicateProductionRequest, reqId, clearpp)
        self.write(result)

    @asyncGen
    def web_delete(self):
        try:
            reqId = self.get_argument("ID")
            reqId = int(json.loads(reqId))
        except Exception:
            self.finish({"success": "false", "result": [], "total": 0, "error": "Request ID is not a number"})
        result = yield self.threadTask(ProductionRequestClient().deleteProductionRequest, reqId)
        self.write(result)

    @asyncGen
    def web_typeandmodels(self):
        types = [(x, x) for x in self.__request_types()]
        result = yield self.threadTask(
            ProductionRequestClient().getProductionRequestList, 0, "RequestID", "DESC", 0, 0, {"IsModel": 1}
        )
        models = []
        if not result["OK"]:
            models = []
        else:
            models = [
                (str(x["RequestID"]), str(x["RequestType"] + " - " + x["RequestName"])) for x in result["Value"]["Rows"]
            ]

        rows = [{"Name": x[0], "Description": x[1]} for x in types + models]
        self.finish({"OK": True, "result": rows, "total": len(rows)})

    @asyncGen
    def web_bkk_dq_list(self):
        result = yield self.threadTask(BookkeepingClient().getAvailableDataQuality)
        if not result["OK"]:
            self.finish({"success": "false", "result": [], "total": 0, "error": result["Message"]})
            return
        value = []
        if result["Value"]:
            value.append({"v": "ALL"})
        for x in result["Value"]:
            value.append({"v": x})
        self.finish({"OK": True, "total": len(value), "result": value})

    @asyncGen
    def web_bkk_event_types(self):
        addempty = "addempty" in self.request.arguments
        result = yield self.threadTask(BookkeepingClient().getAvailableEventTypes)
        if not result["OK"]:
            self.finish({"success": "false", "result": [], "total": 0, "error": result["Message"]})
            return
        rows = []
        for et in result["Value"]:
            rows.append({"id": et[0], "name": et[1], "text": "%s - %s" % (str(et[0]), str(et[1]))})
        rows.sort(key=lambda x: x["id"])
        if addempty:
            rows.insert(0, {"id": 99999999, "name": "", "text": "&nbsp;"})
        self.finish({"OK": True, "result": rows, "total": len(rows)})

    @asyncGen
    def web_bkk_input_tcks(self):
        pars = {
            "EventTypeId": self.get_argument("eventType", ""),
            "ConfigVersion": self.get_argument("configVersion", ""),
            "ProcessingPass": "/" + self.get_argument("inProPass", ""),
            "ConfigName": self.get_argument("configName", ""),
            "ConditionDescription": self.get_argument("simDesc", ""),
        }
        # log.info(str(pars))
        result = yield self.threadTask(BookkeepingClient().getTCKs, pars)
        if not result["OK"]:
            self.finish({"success": "false", "result": [], "total": 0, "error": result["Message"]})
            return
        gLogger.info(result["Value"])
        value = []
        if result["Value"]:
            value.append({"id": 0, "text": "ALL"})
        for x in result["Value"]:
            value.append({"id": str(x), "text": str(x)})
        value.sort(key=lambda x: x["id"])
        self.finish({"OK": True, "total": len(value), "result": value})

    @asyncGen
    def web_bkk_input_prod(self):
        pars = {
            "EventTypeId": self.get_argument("eventType", ""),
            "ConfigVersion": self.get_argument("configVersion", ""),
            "ProcessingPass": "/" + self.get_argument("inProPass", ""),
            "ConfigName": self.get_argument("configName", ""),
            "ConditionDescription": self.get_argument("simDesc", ""),
        }
        gLogger.info(str(pars))
        result = yield self.threadTask(BookkeepingClient().getProductions, pars)
        if not result["OK"]:
            self.finish({"success": "false", "result": [], "total": 0, "error": result["Message"]})
            return
        value = []
        if result["Value"]["Records"]:
            value.append({"id": 0, "text": "ALL"})
        for x in result["Value"]["Records"]:
            prod = x[0]
            if prod < 0:
                prod = -prod
            value.append({"id": prod, "text": prod})
        value.sort(key=lambda x: x["id"])
        self.finish({"OK": True, "total": len(value), "result": value})

    @asyncGen
    def web_bkk_simcond(self):
        result = yield self.threadTask(BookkeepingClient().getSimConditions)
        if not result["OK"]:
            self.finish({"success": "false", "result": [], "total": 0, "error": result["Message"]})
            return
        rows = [dict(zip(self.bkSimCondFields, sc)) for sc in result["Value"]]
        # !!! Sorting and selection must be moved to MySQL/Service side
        result = SelectAndSort(self.request, rows, "simCondID")
        self.finish(result)

    @asyncGen
    def web_getSimCondTree(self):
        _path, rtype, tree, dataQuality = self.__parseRequest()
        node = self.get_argument("node", "")

        bk = LHCB_BKKDBClient(web=True)

        yield self.threadTask(bk.setFileTypes, [])

        bk.setAdvancedQueries(rtype)
        bk.setParameter(tree)
        bk.setDataQualities(dataQuality)

        retVal = yield self.threadTask(bk.list, node)

        nodes = []
        if retVal:
            for i in retVal:
                node = {}
                node["text"] = i["name"]
                node["fullpath"] = i["fullpath"]
                node["id"] = i["fullpath"]
                node["selection"] = i["selection"] if "selection" in i else ""
                node["method"] = i["method"] if "method" in i else ""
                node["cls"] = "folder" if i["expandable"] else "file"
                if "level" in i and i["level"] == "Simulation Conditions/DataTaking":
                    node["cls"] = "file"
                    node["leaf"] = True
                else:
                    node["leaf"] = not i["expandable"]
                if "level" in i:
                    node["level"] = i["level"]
                    node["qtip"] = i["level"]
                nodes += [node]

        result = tornado.escape.json_encode(nodes)
        self.finish(result)

    @asyncGen
    def web_bkk_input_tree(self):
        keep = ["simCondID", "condType", "inProPass", "evType"]
        node = self.get_argument("node", "")

        bkcli = LHCB_BKKDBClient(web=True)

        value = []
        level = ""
        scd = {}
        known = {}

        nodes = yield self.threadTask(bkcli.list, node)
        for item in nodes:
            ipath = item["fullpath"]
            p = ipath.split("/")[1:]
            x = {"id": ipath, "text": p[-1]}
            x.update(dict(zip(["configName", "configVersion"], p[:2])))
            for i in keep:
                if self.get_argument(i, ""):
                    x[i] = self.get_arguments(i)
            if "level" in item:
                level = item["level"]
            if level == "Simulation Conditions/DataTaking":
                result = self.__condFromPath(ipath, bkcli, item)
                if not result["OK"]:
                    raise WErr.fromSERROR(result)
                x.update(result["Value"])
            elif level == "Processing Pass":
                if x.get("inProPass", ""):
                    x["inProPass"] = x["inProPass"][-1] + "/" + p[-1]
                else:
                    x["inProPass"] = p[-1]
            elif level == "Event types":
                x["evType"] = p[-1]
            elif level == "FileTypes":
                x["leaf"] = True
                x["inFileType"] = p[-1]
                if not scd:
                    result = self.__condFromPath(ipath, bkcli, {})
                    if not result["OK"]:
                        raise WErr.fromSERROR(result)
                    scd = result["Value"]
                x.update(scd)
            if x["text"] in known:
                gLogger.error("Duplicated entry: %s %s" % (str(known[x["text"]]), str(x)))
            else:
                known[x["text"]] = x
                value.append(x)
        result = tornado.escape.json_encode(value)
        self.finish(result)

    @asyncGen
    def web_save(self):
        rdict = {k: self.get_arguments(k, strip=False) for k in self.request.arguments}
        self.__unescape(rdict)

        # Make it backward compatible
        for x in ["inTCKs"]:
            if x in rdict and str(rdict[x]) == "0":
                del rdict[x]
        reqId = ""
        if "ID" in rdict:
            try:
                reqId = int(rdict["ID"])
            except Exception:
                self.finish({"success": "false", "result": [], "total": 0, "error": "Request ID is not a number"})
                return
            del rdict["ID"]
            req = self.__fromlocal(rdict)
            result = yield self.threadTask(ProductionRequestClient().updateProductionRequest, reqId, req)
        else:
            sData = self.getSessionData()

            user = sData["user"]["username"]

            rdict["RequestAuthor"] = user
            req = self.__fromlocal(rdict)
            result = yield self.threadTask(ProductionRequestClient().createProductionRequest, req)

        if result["OK"]:
            self.finish({"success": "true", "requestId": reqId})
        else:
            raise WErr.fromSERROR(result)
        # self.finish()

    @asyncGen
    def web_templates(self):
        ret = yield self.threadTask(ProductionRequestClient().getProductionTemplateList)
        if not ret["OK"]:
            raise WErr.fromSERROR(ret)

        value = []
        for x in ret["Value"]:
            if "_run.py" not in x["WFName"]:
                gLogger.error("Skipping invalid production request template name:", x["WFName"])
                continue
            x["Type"] = "Script"
            value.append(x)
        result = {"OK": True, "total": len(value), "result": value}

        self.finish(result)

    def getRequestFields(self):
        result = dict.fromkeys(self.localFields, None)
        result.update(dict.fromkeys(self.simcondFields))
        result.update(dict.fromkeys(self.extraFields))
        for x in self.proStepFields:
            for i in range(1, 20):
                result["p%d%s" % (i, x)] = None
        sData = self.getSessionData()

        result["userName"] = sData["user"]["username"]
        result["userDN"] = sData["user"]["DN"]
        return result

    @asyncGen
    def web_template_parlist(self):
        tpl_name = self.get_argument("tpl", "")
        result = yield self.threadTask(ProductionRequestClient().getProductionTemplate, tpl_name)
        if not result["OK"]:
            raise WErr.fromSERROR(result)
        text = result["Value"]
        tpl = PrTpl(text)
        rqf = self.getRequestFields()
        tpf = tpl.getParams()
        tpd = tpl.getDefaults()
        plist = []
        for x in tpf:
            if x not in rqf:
                plist.append({"par": x, "label": tpf[x], "value": tpd[x].split("^")[0], "default": tpd[x]})
        self.finish({"OK": True, "total": len(plist), "result": plist})

    def getProductionRequest(self, ids):
        result = ProductionRequestClient().getProductionRequest(ids)
        if not result["OK"]:
            return result
        rr = result["Value"]
        lr = {}
        for x in rr:
            lr[x] = self.__2local(rr[x])
        return S_OK(lr)

    def getProductionRequestList(self, parent):
        try:
            offset = int(self.__getArgument("start", 0))
            limit = int(self.__getArgument("limit", 0))
            sortlist = self.__getJsonArgument("sort", [])
            if sortlist:
                sortBy = str(sortlist[-1]["property"])
                sortBy = self.serviceFields[self.localFields.index(sortBy)]
                sortOrder = str(sortlist[-1]["direction"])
            else:
                sortBy = self.serviceFields[self.localFields.index("ID")]
                sortOrder = "DESC"

            filterOpts = {}
            for x, y in [
                ("typeF", "RequestType"),
                ("stateF", "RequestState"),
                ("authorF", "RequestAuthor"),
                ("idF", "RequestID"),
                ("modF", "IsModel"),
                ("wgF", "RequestWG"),
            ]:

                val = self.get_argument(x, "")

                if val != "":
                    val = list(json.loads(val))
                    if val:
                        if not isinstance(val[0], bool):
                            filterOpts[y] = ",".join(val)
                        else:
                            filterOpts[y] = val[-1]

            if "IsModel" in filterOpts:
                if filterOpts["IsModel"]:
                    filterOpts["IsModel"] = 1
                else:
                    filterOpts["IsModel"] = 0
        except Exception as e:
            raise WErr(404, "Badly formatted list request: %s" + str(e))

        result = ProductionRequestClient().getProductionRequestList(
            parent, sortBy, sortOrder, offset, limit, filterOpts
        )

        if not result["OK"]:
            raise WErr.fromSERROR(result)

        rows = [self.__2local(x) for x in result["Value"]["Rows"]]
        aet = BookkeepingClient().getAvailableEventTypes()
        if aet["OK"]:
            etd = {}
            for et in aet["Value"]:
                etd[str(et[0])] = str(et[1])
            for x in rows:
                if "eventType" in x:
                    x["eventText"] = etd.get(str(x["eventType"]), "")

        return {"OK": True, "result": rows, "total": result["Value"]["Total"]}

    @asyncGen
    def web_create_workflow(self):
        """!!! Note: 1 level parent=master assumed !!!"""
        rdict = {k: self.get_argument(k) for k in self.request.arguments}
        for x in ["RequestID", "Template", "Subrequests"]:
            if x not in rdict:
                raise WErr(404, "Required parameter %s is not specified" % x)

        try:
            reqId = int(rdict["RequestID"])
            tpl_name = self.get_argument("Template")
            operation = self.get_argument("Operation", "Simple")
            sstr = self.get_argument("Subrequests")
            if sstr:
                slist = [int(x) for x in sstr.split(",")]
            else:
                slist = []
            sdict = dict.fromkeys(slist, None)
            del rdict["RequestID"]
            del rdict["Template"]
            del rdict["Subrequests"]
            if "Operation" in rdict:
                del rdict["Operation"]
        except Exception as e:
            raise WErr(404, "Wrong parameters (%s)" % str(e))
        requests = []
        if "RequestIDs" in rdict:
            requests = json.loads(rdict["RequestIDs"])
        if requests:
            res = []
            for reqId in requests:
                reqId = int(reqId)
                retVal = yield self.threadTask(self.__createScript, rdict, reqId, operation, tpl_name, sdict)
                if retVal["OK"]:
                    res += [val for val in retVal["Value"]]
                else:
                    raise WErr(
                        404, "The following error occurred during the production creation: %s" % retVal["Message"]
                    )
                if operation == "ScriptPreview":
                    break
            self.finish(S_OK(res))
        else:
            retVal = yield self.threadTask(self.__createScript, rdict, reqId, operation, tpl_name, sdict)
            if not retVal["OK"]:
                raise WErr(404, "The following error occurred during the production creation: %s" % retVal["Message"])
            self.finish(retVal)

    def __createScript(self, rdict, reqId, operation, tpl_name, sdict):
        """
        This method is used to create production or view the script using a certain template
        :param dict rdict: contains the production parameters
        :param int reqId: request id
        :param str operation: script previre or generate the production
        :param str tpl_name: template name use to create the workflow
        :param dict sdict: sub request parameters
        :return: S_OK(requestID:int, Body:list}
        """
        ret = ProductionRequestClient().getProductionTemplate(tpl_name)
        if not ret["OK"]:
            raise WErr.fromSERROR(ret)
        tpl = PrTpl(ret["Value"])

        ret = self.getProductionRequest([reqId])
        if not ret["OK"]:
            raise WErr.fromSERROR(ret)
        rqdict = ret["Value"][reqId]
        dictlist = []
        if rqdict["_is_leaf"]:
            d = self.getRequestFields()
            d.update(rqdict)
            d.update(rdict)
            dictlist.append(d)
        else:
            if not sdict:
                raise WErr(404, "Subrequests are not specified (but required)")
            ret = self.getProductionRequestList(reqId)
            if not ret["OK"]:
                raise WErr.fromSERROR(ret)
            for x in ret["result"]:
                if x["ID"] not in sdict:
                    continue
                d = self.getRequestFields()
                d.update(rqdict)
                for y in x:
                    if x[y]:
                        d[y] = x[y]
                d.update(rdict)
                dictlist.append(d)
        success = []
        fail = []
        for x in dictlist:
            for y in x:
                if x[y] is None:
                    x[y] = ""
                else:
                    x[y] = str(x[y])
            body = tpl.apply(x)
            if operation != "Generate":
                success.append({"ID": x["ID"], "Body": body})
            else:
                try:
                    res = ProductionRequestClient().execProductionScript(body, "")
                    if res["OK"]:
                        success.append({"ID": x["ID"], "Body": res["Value"]})
                    else:
                        fail.append(str(x["ID"]))
                except Exception:
                    fail.append(str(x["ID"]))
            continue  # not working with WF DB for now
            # name = 'PRQ_%s' % x['ID']
            # wf = fromXMLString( tpl.apply( x ) )
            # wf.setName( name )
            # wf.setType( 'production/requests' )
            # try:
            #   wfxml = wf.toXML()
            #   result = yield self.threadTask( ProductionRequestClient().publishWorkflow, str( wfxml ), True )
            # except Exception, msg:
            #   result = {'OK':False, 'Message': str( msg )}
            # if not result['OK']:
            #   fail.append( str( x['ID'] ) )
            # else:
            #   success.append( str( x['ID'] ) )

        if fail:
            raise WErr(404, "Couldn't get results from %s." % (",".join(fail)))
        else:
            # return S_OK("Success with %s" % ','.join(success))
            return S_OK(success)

    @asyncGen
    def web_split(self):
        try:
            reqId = int(self.get_argument("ID"))
            slist = list(json.loads(self.get_argument("Subrequests")))
        except Exception as e:
            raise WErr(400, "Wrong parameters (%s)" % str(e))

        result = yield self.threadTask(ProductionRequestClient().splitProductionRequest, reqId, slist)
        self.finish(result)

    @asyncGen
    def web_progress(self):
        try:
            reqId = int(self.get_argument("RequestID", "0"))
        except Exception:
            raise WErr(500, "Request ID is not a number")
        result = yield self.threadTask(ProductionRequestClient().getProductionProgressList, reqId)
        if not result["OK"]:
            raise WErr.fromSERROR(result)
        self.finish({"OK": True, "result": result["Value"]["Rows"], "total": result["Value"]["Total"]})

    @asyncGen
    def web_add_production(self):
        try:
            requestID = int(self.get_argument("RequestID"))
            productionID = int(self.get_argument("ProductionID"))
        except Exception:
            raise WErr(500, "Incorrect Request or production ID")

        result = yield self.threadTask(self.__bkProductionProgress, productionID)
        bkEvents = 0 if not result["OK"] else result["Value"]
        result = yield self.threadTask(
            ProductionRequestClient().addProductionToRequest,
            {"ProductionID": productionID, "RequestID": requestID, "Used": 1, "BkEvents": bkEvents},
        )
        self.finish(result)

    @asyncGen
    def web_remove_production(self):
        try:
            productionID = int(self.get_argument("ProductionID"))
        except ValueError:
            raise WErr(400, "Production ID is not a number")

        result = yield self.threadTask(ProductionRequestClient().removeProductionFromRequest, productionID)
        self.finish(result)

    @asyncGen
    def web_use_production(self):
        try:
            productionID = int(self.get_argument("ProductionID"))
            used = bool(int(self.get_argument("Used", "0")))
        except ValueError:
            raise WErr(400, "Incorrect Production ID use Used flag")

        result = yield self.threadTask(ProductionRequestClient().useProductionForRequest, productionID, used)
        self.finish(result)

    @asyncGen
    def web_productions(self):
        try:
            prId = int(self.get_argument("RequestID"))
        except ValueError:
            raise WErr(400, "Request ID is not a number")

        result = yield self.threadTask(ProductionRequestClient().getProductionList, prId)
        if not result["OK"]:
            raise WErr.fromSERROR(result)
        self.finish({"OK": True, "result": result["Value"], "total": len(result["Value"])})

    @asyncGen
    def web_getRequest(self):
        stepId = self.get_argument("StepId")
        requests = ProductionRequestManagerHandler.__dataCache.get("allData")
        if not requests:
            retVal = yield self.threadTask(
                ProductionRequestClient().getProductionRequestList, 0, "", "", 0, 0, {"RequestType": "Simulation"}
            )
            if not retVal["OK"]:
                raise WErr.fromSERROR(retVal)
            requests = retVal["Value"].get("Rows", [])
            ProductionRequestManagerHandler.__dataCache.add("allData", 3600, requests)

        records = []
        for request in requests:
            if request.get("ProDetail") and str(stepId) in request.get("ProDetail", ""):
                record = {}
                record["RequestId"] = request["RequestID"]
                record["RequestName"] = request["RequestName"]
                record["RequestWG"] = request["RequestWG"]
                record["RequestAuthor"] = request["RequestAuthor"]
                records.append(record)
        self.finish(
            {
                "success": "true",
                "result": records,
                "total": len(records),
                "date": Time.dateTime().strftime("%Y-%m-%d %H:%M [UTC]"),
            }
        )

    @asyncGen
    def web_getFastSimulationOpts(self):
        """

        This method used by the "Fast simulation type" combo box. The values of the combo box is filled using the CS

        """

        fastsimTypes = ["None", "Redecay"]
        csS = PathFinder.getServiceSection("ProductionManagement/ProductionRequest")
        if csS:
            fastsimTypes = gConfig.getValue("%s/FastSimulationType" % csS, fastsimTypes)

        rows = [{"text": i, "name": i} for i in fastsimTypes]
        self.finish({"OK": True, "result": rows, "total": len(rows)})
