from typing import Optional, List, Dict
import fnmatch
import os
import re
import ROOT

import pandas as pd

class RooProcAction(object):
    def __init__(self, **params):
        self._params = params
        self.executed = False
        self.status   = None
    
    def get_formatted_parameters(self, global_vars:Optional[Dict]=None):
        if global_vars is None:
            global_vars = {}
        formatted_parameters = {}
        for k,v in self._params.items():
            if v is None:
                formatted_parameters[k] = None
                continue
            k_literals = re.findall(r"\${(\w+)}", k)
            if isinstance(v, list):
                v = '__SEPARATOR__'.join(v)
            v_literals = re.findall(r"\${(\w+)}", v)
            all_literals = set(k_literals).union(set(v_literals))
            for literal in all_literals:
                if literal not in global_vars:
                    raise RuntimeError(f"the substitute literal `{literal}` is undefined")
            for literal in k_literals:
                substitute = global_vars[literal]
                k = k.replace("${" + literal + "}", str(substitute))
            for literal in v_literals:
                substitute = global_vars[literal]
                v = v.replace("${" + literal + "}", str(substitute))
            if '__SEPARATOR__' in v:
                v = v.split("__SEPARATOR__")
            formatted_parameters[k] = v
        return formatted_parameters
    
    def makedirs(self, fname):
        dirname = os.path.dirname(fname)
        if dirname and (not os.path.exists(dirname)):
            os.makedirs(dirname)

    def _execute(self, rdf, **kwargs):
        return rdf
    
    def execute(self, rdf, global_vars:Optional[Dict]=None):
        params = self.get_formatted_parameters(global_vars)
        rdf_next = self._execute(rdf, **params)
        self.executed = True
        return rdf_next
    
    @classmethod
    def parse_as_kwargs(cls, text):
        kwargs = {}
        text = re.sub(r"\s*", "", text)
        list_attributes = re.findall(r"(\w+)=\[([^\[\]]+)\]", text)
        for attribute in list_attributes:
            kwargs[attribute[0]] = attribute[1].split(",")
            text = text.replace(f"{attribute[0]}=[{attribute[1]}]","")
        attributes = re.findall(r"(\w+)=([^,]+)", text)
        for attribute in attributes:
            kwargs[attribute[0]] = attribute[1]
        return kwargs
    
    @classmethod
    def parse(cls, text):
        raise NotImplementedError
    
class RooProcTreeName(RooProcAction):
    
    def __init__(self, treename:str):
        super().__init__(treename=treename)
        
    @classmethod
    def parse(cls, text):
        return cls(treename=text)
    
class RooProcExport(RooProcAction):
    def __init__(self, filename:str):
        super().__init__(filename=filename)
        
    @classmethod
    def parse(cls, text):
        kwargs = cls.parse_as_kwargs(text)
        return cls(**kwargs)
    
class RooProcGlobalVariables(RooProcAction):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    @classmethod
    def parse(cls, text):
        text = re.sub(r"\s*", "", text)
        tokens = text.split(",")
        globs = {}
        for token in tokens:
            result = re.match("^(\w+)=(.*)", token)
            if not result:
                raise RuntimeError(f"invalid expression {token}")
            globs[result[1]] = result[2]
        return cls(**globs)
    
class RooProcDefine(RooProcAction):
    
    def __init__(self, name:str, expression:str):
        super().__init__(name=name, expression=expression)
        
    @classmethod
    def parse(cls, text):
        result = re.search(r"^\s*(\w+)\s*=(.*)", text)
        if not result:
            raise RuntimeError(f"invalid expression {text}")
        name = result.group(1)
        expression = result.group(2)
        return cls(name=name, expression=expression)        
        
    def _execute(self, rdf, **kwargs):
        name = kwargs['name']
        expression = kwargs['expression']
        rdf_next = rdf.Define(name, expression)
        return rdf_next
    
class RooProcFilter(RooProcAction):
    def __init__(self, expression:str, name:Optional[str]=None):
        super().__init__(expression=expression,
                         name=name)
        
    @classmethod
    def parse(cls, text):
        name_literals = re.findall(r"@{([^{}]+)}", text)
        if len(name_literals) == 0:
            name = None
            expression = text.strip()
        elif len(name_literals) == 1:
            name = name_literals[0]
            expression = text.replace("@{" + name + "}", "").strip()
        else:
            raise RuntimeError(f"multiple filter names detected in the expression `{text}`")
        return cls(name=name, expression=expression)
        
    def _execute(self, rdf, **kwargs):
        expression = kwargs['expression']
        name = kwargs.get("name", None)
        if name is not None:
            rdf_next = rdf.Filter(expression, name)
        else:
            rdf_next = rdf.Filter(expression)
        return rdf_next
    
class RooProcSave(RooProcAction):
    
    def __init__(self, treename:str, filename:str, 
                 columns:Optional[List[str]]=None,
                 frame:Optional[str]=None):
        super().__init__(treename=treename,
                         filename=filename,
                         columns=columns,
                         frame=frame)
        
    @classmethod
    def parse(cls, text):
        kwargs = cls.parse_as_kwargs(text)
        return cls(**kwargs)
    
    def _execute(self, rdf, **kwargs):
        treename = kwargs['treename']
        filename = kwargs['filename']
        columns = kwargs.get('columns', None)
        if columns is None:
            rdf_next = rdf.Snapshot(treename, filename)
        else:
            all_columns = [str(c) for c in rdf.GetColumnNames()]
            save_columns = []
            for column in columns:
                save_columns += [c for c in all_columns if fnmatch.fnmatch(c, column)]
            save_columns = list(set(save_columns))
            self.makedirs(filename)
            rdf_next = rdf.Snapshot(treename, filename, save_columns)
        return rdf_next
    
class RooProcReport(RooProcAction):
    def __init__(self, display:bool=False, filename:Optional[str]=None):
        super().__init__(display=display,
                         filename=filename)
    @classmethod
    def parse(cls, text):
        kwargs = cls.parse_as_kwargs(text)
        return cls(**kwargs)
    
    def _execute(self, rdf, **kwargs):
        display = kwargs['display']
        filename = kwargs['filename']
        cut_report = rdf.Report()
        result = []
        cumulative_eff  = 1
        for report in cut_report:
            data = {}
            data['name'] = report.GetName()
            data['all']  = report.GetAll()
            data['pass'] = report.GetPass()
            data['efficiency'] = report.GetEff()
            cumulative_eff *= data['efficiency']/100
            data['cumulative_efficiency'] = cumulative_eff*100
            result.append(data)
        df = pd.DataFrame(result)
        if int(display):
            print(df)
        if filename is not None:
            self.makedirs(filename)
            df.to_csv(filename)
        return rdf
    
class RooProcSum(RooProcAction):
    def __init__(self, ext_var_name:str, column_name:str):
        super().__init__(ext_var_name=ext_var_name,
                         column_name=column_name)
        self.ext_var = {}
    @classmethod
    def parse(cls, text):
        name_literals = re.findall(r"@{([^{}]+)}", text)
        if len(name_literals) == 1:
            ext_var_name = name_literals[0]
            column_name = text.replace("@{" + ext_var_name + "}", "").strip()
        else:
            raise RuntimeError("unspecified external variable name (format:@{ext_var_name})")
        return cls(ext_var_name=ext_var_name, column_name=column_name)
        
    def _execute(self, rdf, **kwargs):
        ext_var_name = kwargs['ext_var_name']
        column_name = kwargs['column_name']
        self.ext_var[ext_var_name] = rdf.Sum(column_name)
        return rdf
        
class RooProcDeclare(RooProcAction):
    
    def __init__(self, expression:str, name:Optional[str]=None):
        super().__init__(expression=expression,
                         name=name)
        
    @classmethod
    def parse(cls, text):
        return cls(expression=text)        
        
    @staticmethod
    def create_declaration(expression:str, name:Optional[str]=None):
        if name is None:
            hash_str = str(hash(expression)).replace("-", "n")
            name_guard = f"__RooProcDeclare_{hash_str}__"
        else:
            name_guard = f"__RooProcDeclare_{name}__"
        guarded_declaration = f"#ifndef {name_guard}\n"
        guarded_declaration += f"#define {name_guard}\n"
        guarded_declaration += f"\n{expression}\n\n#endif\n"
        return guarded_declaration
    
    @staticmethod
    def declare_expression(expression:str, name:Optional[str]=None):
        declaration = RooProcDeclare.create_declaration(expression, name)
        status = ROOT.gInterpreter.Declare(declaration)
        return status
    
    def _execute(self, rdf, **kwargs):
        name = kwargs.get("name", None)
        expression = kwargs['expression']
        self.declare_expression(expression, name)
        return rdf
    
class RooProcSaveFrame(RooProcAction):
    def __init__(self, name:str):
        super().__init__(name=name)

    @classmethod
    def parse(cls, text):
        return cls(name=text)
    
class RooProcLoadFrame(RooProcAction):
    def __init__(self, name:str):
        super().__init__(name=name)

    @classmethod
    def parse(cls, text):
        return cls(name=text)    
    

ACTION_MAP = {
    'TREENAME': RooProcTreeName,
    'DECLARE': RooProcDeclare,
    'GLOBAL': RooProcGlobalVariables,
    'DEFINE': RooProcDefine,
    'FILTER': RooProcFilter,
    'SAVE': RooProcSave,
    'REPORT': RooProcReport,
    'GETSUM': RooProcSum,
    'EXPORT': RooProcExport,
    'SAVE_FRAME': RooProcSaveFrame,
    'LOAD_FRAME': RooProcLoadFrame
}