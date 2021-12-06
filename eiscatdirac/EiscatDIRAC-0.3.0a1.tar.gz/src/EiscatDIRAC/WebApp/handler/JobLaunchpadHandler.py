import pprint

from DIRAC import gLogger
from DIRAC.Resources.Catalog.FileCatalog import FileCatalog
from DIRAC.ConfigurationSystem.Client.Helpers.Registry import getVOForGroup
from DIRAC.ConfigurationSystem.Client.Helpers.Operations import Operations

from WebAppDIRAC.Lib.WebHandler import WebHandler, asyncGen
from WebAppDIRAC.WebApp.handler.JobLaunchpadHandler import JobLaunchpadHandler as JobLaunchpad


class JobLaunchpadHandler(JobLaunchpad):
    def __init__(self, *args, **kwargs):
        super(JobLaunchpadHandler, self).__init__(*args, **kwargs)
        sessionData = self.getSessionData()
        for opt, value in (self.getAppSettings().get("Options") or {}).items():
            self.defaultParams[opt] = value.replace(", ", ",").split(",")
        self.user = sessionData["user"].get("username", "")
        self.group = sessionData["user"].get("group", "")
        self.vo = getVOForGroup(self.group)

    @asyncGen
    def web_getLaunchpadSetupWithLFNs(self):
        """Method obtain launchpad setup with pre-selected LFNs as input data parameter,
        the caller js client will use setup to open an new Launchpad
        """
        # On the fly file catalog for advanced launchpad
        if not hasattr(self, "fc"):
            userData = self.getSessionData()
            group = str(userData["user"]["group"])
            vo = getVOForGroup(group)
            self.fc = FileCatalog(vo=vo)

        self.set_header("Content-type", "text/plain")
        arguments = self.request.arguments
        gLogger.always("submit: incoming arguments %s to getLaunchpadSetupWithLFNs" % arguments)
        lfnList = str(arguments["path"][0]).split(",")

        # Modified for Eiscat
        # Checks if the experiments folder in lfn list has a rtg_def.m file at some subfolder
        gLogger.always("submit: checking if some rtg_def.m", arguments)
        processed = []
        metaDict = {"type": "info"}
        for lfn in lfnList:
            pos_relative = lfn.find("/")
            pos_relative = lfn.find("/", pos_relative + 1)
            pos_relative = lfn.find("/", pos_relative + 1)
            pos_relative = lfn.find("/", pos_relative + 1)
            pos_relative = lfn.find("/", pos_relative + 1)
            experiment_lfn = lfn[0:pos_relative]
            if experiment_lfn in processed:
                continue
            processed.append(experiment_lfn)
            gLogger.always("checking rtg_def.m in %s" % experiment_lfn)
            result = self.fc.findFilesByMetadata(metaDict, path=str(experiment_lfn))
            if not result["OK"] or not result["Value"]:
                gLogger.error("Failed to get type info from %s, %s" % (experiment_lfn, result["Message"]))
                continue
            for candidate_lfn in result["Value"]:
                if candidate_lfn.find("rtg_def.m") > 0:
                    lfnList.append(candidate_lfn)
        # End modified

        ptlfn = ""
        for lfn in lfnList:
            ptlfn += (", " + lfn) if ptlfn else lfn

        params = self.defaultParams.copy()
        params["InputData"] = [1, ptlfn]

        obj = Operations(vo=vo)
        predefinedSets = {}
        launchpadSections = obj.getSections("Launchpad")
        if launchpadSections["OK"]:
            for section in launchpadSections["Value"]:
                predefinedSets[section] = {}
                sectionOptions = obj.getOptionsDict("Launchpad/" + section)
                pprint.pprint(sectionOptions)
                if sectionOptions["OK"]:
                    predefinedSets[section] = sectionOptions["Value"]

        self.write({"success": "true", "result": params, "predefinedSets": predefinedSets})
