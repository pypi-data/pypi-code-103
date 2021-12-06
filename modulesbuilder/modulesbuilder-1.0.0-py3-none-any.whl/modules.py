#
# Routines for manipulating groups of module objects
#
import yaml

from .module import Module
from .module import dropDuplicates

DEBUG_GET_MODULES = 0
DEBUG_PROVIDES = 0

# each module must be unique and have the required fields
def validModule(module, modules):
    if not module.valid():
        return 0

    # first module
    if len(modules) == 0:
        return 1

    # valid as long as modules differ by at least one field
    for mod in modules:
        if mod == module:
            return 0
    return 1

def getModuleByID(modID, modules):
    for module in modules:
        if (module.id() == modID):
            return module
    return ""

# Determine the modules provided by module
# Return list of moduleIDs
def moduleProvides(module, modules):
    if DEBUG_PROVIDES: print("moduleProvides %s:" %(module.id()))
    provides = []
    modID = module.id()
    for mod in modules:
        depends = mod.dependsAll()
        for dep in depends:
            if (dep == modID):
                provides += [mod.id()]
                break;
    return dropDuplicates(provides)

# Return list of moduleIDs
def moduleProvidesDeepRec(module, modules, provides):
    if DEBUG_PROVIDES: print("moduleProvidesDeepRec %s:" %(module.id()))
    newProvides = moduleProvides(module, modules)
    if newProvides:
        if DEBUG_PROVIDES: print("%s provides: %s" %(module.id(), newProvides))
        provides += newProvides
        for pro in newProvides:
            provides = moduleProvidesDeepRec(getModuleByID(pro, modules), modules, provides)
    return provides

# Find all modules that directory or indirectly depend on on this module
# Return list of moduleIDs
def moduleProvidesDeep(module, modules):
    if DEBUG_PROVIDES: print("moduleProvidesDeep %s:" %(module.id()))
    return dropDuplicates(moduleProvidesDeepRec(module, modules, []))

# parse out all possible modules from the yaml configuration
def getModules(configFile):
    f = open(configFile, "r")
    data = yaml.safe_load(f)
    rootModule = Module("")
    modules = []
    if 'module' in data:
        data['module']['config'] = configFile
        rootModule = Module(data['module'])
        if validModule(rootModule, modules):
            modules.append(rootModule)
            if DEBUG_GET_MODULES: print("found root module %s" %(rootModule.id()))
        else:
            if DEBUG_GET_MODULES: print("invalid root module: %s" %(rootModule))
    # Parse out any submodules and inherit keys from the rootModule
    if 'module' in rootModule.yml:
        for yml in rootModule.yml['module']:
            try:
                m = Module(yml)
                m.inherit(rootModule)
            except:
                print("Parse error, did you forget to make modules an array?")
                return []
            if validModule(m, modules):
                modules.append(m)
                if DEBUG_GET_MODULES: print("found submodule %s" %(m.id()))
            else:
                if DEBUG_GET_MODULES: print("invalid module:")
                print(m)
            # TODO recursive add modules
            #if 'module' in m:
            #    modules += (getModules(m))
    else:
        if DEBUG_GET_MODULES: print("No submodules found")
    return modules
