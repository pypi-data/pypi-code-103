from typing import Optional, List, Dict, Union
import os
import time
import ROOT

from .builtin_methods import BUILTIN_METHODS
from .actions import *
from .parsers import RooProcConfigParser

from quickstats.components import AbstractObject

class RooProcessor(AbstractObject):
    def __init__(self, config_path:Optional[str]=None,
                 multithread:bool=True,
                 verbosity:Optional[Union[int, str]]="INFO"):
        super().__init__(verbosity=verbosity)
        self.action_list = []
        self.rdf_snapshots = {}
        self.rdf = None
        self.global_variables = {}
        self.treename = None
        
        self.load_buildin_functions()
        
        if multithread:
            ROOT.EnableImplicitMT()
        
        if config_path is not None:
            self.load_config(config_path)
            
    def load_buildin_functions(self):
        for name, definition in BUILTIN_METHODS.items():
            RooProcDeclare.declare_expression(definition, name)
    
    def load_config(self, config_path:Optional[str]=None):
        action_list = RooProcConfigParser.parse_file(config_path)
        if len(action_list) == 0:
            raise RuntimeError("no actions found in the process card")
        first_action = action_list[0]
        if not isinstance(first_action, RooProcTreeName):
            raise RuntimeError("tree name must be specified at the beginning of the process card")
        self.treename = first_action._params['treename']
        self.action_list = action_list
    
    def run(self, filename:str):
        if not os.path.exists(filename):
            raise FileNotFoundError(f"file `{filename}` does not exist")
        self.stdout.info(f"INFO: Processing file `{filename}`.")
        if len(self.action_list) == 0:
            self.stdout.warning("WARNING: No actions to be performed.")
            return None
        if self.treename is None:
            raise RuntimeError("tree name is undefined")
        start = time.time()
        self.rdf = ROOT.RDataFrame(self.treename, filename)
        for i, action in enumerate(self.action_list):      
            if isinstance(action, RooProcGlobalVariables):
                self.global_variables.update(action._params)
            else:
                self.rdf = action.execute(self.rdf, self.global_variables)
                if isinstance(action, RooProcSave):
                    params = action.get_formatted_parameters(self.global_variables)
                    filename = params['filename']
                    self.stdout.info(f"INFO: Writing output to `{filename}`.")
        end = time.time()
        time_taken = end - start
        self.stdout.info(f"INFO: Task finished. Total time taken: {time_taken:.3f} s.")