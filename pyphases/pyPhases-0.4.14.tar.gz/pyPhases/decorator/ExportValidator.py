
from ..Phase import Phase
from .Decorator import Decorator

class ExportValidator(Decorator):
    """An example decorator that checks if all config defined exports are actually exported during the run of the phase
    """

    def filter(self, phase : Phase) -> bool:
        """ the decorator should only be executed if the phase should export any data
        """
        self.logDebug("The phase %s has %s exports"%(phase.name, len(phase.exportData)))
        return len(phase.exportData) > 0

    def after(self, phase : Phase):
        """ after the phase is execute, check if all exported data is registered within the project
        """
        project = phase.project
        missingDataNames = []
        for data in phase.exportData:
            if(not project.dataExists(data)):
                missingDataNames.append(data.name)

        if len(missingDataNames) > 0 :
            self.logWarning("The phase %s did not export: %s"%(phase.name, missingDataNames))

