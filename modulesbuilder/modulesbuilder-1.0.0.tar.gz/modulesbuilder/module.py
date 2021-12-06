#
# Define the module dictionary object and useful routines
#
import glob
import os
import yaml

# Used for indentation gobally
INDENT = "  "

# Modules can be defined for operating systems, architectures, etc.
# NOTE: order of fields must be consistent and determines the nesting order
# in the modulefile switch:case structure.
unameFields = []
unameFields += ['machine']     # the arch, e.g. x86_64
unameFields += ['sysname']     # the operating system name
unameFields += ['os_release']  # the operating system release
unameFields += ['os_version']  # the operating system version
unameFields += ['domain']      # the name of the domain
unameFields += ['nodename']    # the hostname

def legacyModuleTarget(yml):
    return yml['name'] + '-' + yml['version'] + '-' + yml['machine']

def dropDuplicates(array):
    if array:
        return list(set(array))
    else:
        return array

def toList(obj):
    if not isinstance(obj, list):
        return [obj]
    else:
        return obj

class Module:
    # initialize module from yaml dictionary dump
    def __init__(self, yml):
        self.yml = yml
        self.type = ""
        self.path = "" #path relative to the modules prefix

    def __repr__(self):
        return self.yml.__repr__()

    def __str__(self):
        # TODO pretty print
        return self.yml.__str__()

    # Equality is defined up to the ability to distinguish between sections in
    # a modulefile separated by uname fields
    def __eq__(self, other):
        if self.name() != other.name():
            return 0
        if self.version() != other.version():
            return 0
        for field in unameFields:
            if field in self.yml and field in other.yml:
                if self.yml[field] != other.yml[field]:
                    return 0
        return 1

    # Fill in missing fields in submodule from the parent module
    def inherit(self, other):
        for field in other.yml.keys():
            # Do not inherit certain fields set on a per-module basis
            if field == "set_default":
                continue
            if not field in self.yml:
                self.yml[field] = other.yml[field]

    # Modules must at least have a name and version
    def valid(self):
        if self.id(): return 1
        else: return 0

    #
    # Getters and setters to interface the underlying dictionary
    #
    def name(self):
        try: return self.yml['name']
        except: return ""

    def setname(self,name):
        self.yml['name'] = name

    def version(self):
        try: return self.yml['version']
        except: return ""

    def setversion(self,version):
        self.yml['version'] = version

    # module ID suitable for IO, e.g collapse paths
    def idIO(self):
        return self.id.replace("/", "-")

    # unique self.yml identifier
    def id(self):
        if 'name' in self.yml and 'version' in self.yml:
            return "%s/%s" %(self.yml['name'], self.yml['version'])
        else:
            return ""

    def dockerfile(self):
        try: return self.yml['dockerfile']
        except: return "Dockerfile"

    def setdockerfile(self,dockerfile):
        self.yml['dockerfile'] = dockerfile

    def machine(self):
        try: return self.yml['machine']
        except: return ""

    def setmachine(self,machine):
        self.yml['machine'] = machine

    def website(self):
        try: return self.yml['website']
        except: return ""

    def setwebsite(self,website):
        self.yml['website'] = website

    def prefix(self):
        try: return self.yml['prefix']
        except: return ""

    def setprefix(self,prefix):
        self.yml['prefix'] = prefix

    def body(self):
        try: return self.yml['modulefile_body']
        except: return ""

    def setbody(self,body):
        self.yml['modulefile_body'] = body

    def help(self):
        try: return self.yml['modulefile_help']
        except: return ""

    def sethelp(self,help):
        self.yml['modulefile_help'] = help

    def depends(self):
        depends = []
        if 'dependencies' in self.yml:
            depends += self.yml['dependencies']
        if depends:
            depends = dropDuplicates(depends)
            depends.sort()
        return depends

    def setdepends(self, depends):
        self.yml['dependencies'] = depends

    def dependsSticky(self):
        depends = []
        if 'dependencies_no_unload' in self.yml:
            depends += self.yml['dependencies_no_unload']
        if depends:
            depends = dropDuplicates(depends)
            depends.sort()
        return depends

    def setdependsSticky(self, depends):
        self.yml['dependencies_no_unload'] = depends

    # Return the modules ID's of `
    def dependsAll(self):
        depends = []
        if 'dependencies' in self.yml:
            depends += self.yml['dependencies']
        if 'dependencies_no_unload' in self.yml:
            depends += self.yml['dependencies_no_unload']
        if depends:
            depends = dropDuplicates(depends)
            depends.sort()
        return depends

    # Files associated with self.yml definition and build
    def files(self):
        files = []
        # Must include the containing yaml config
        if 'config' in self.yml:
            files += [self.yml['config']]

        # specified files overrides defaults
        if 'files' in self.yml:
            files += self.yml['files']
        else:
            # Default files
            try:
                buildDir = "build/%s" %(self.name())
                if os.path.isdir(buildDir):
                    files += glob.glob(buildDir + "/**", recursive=True)
                script = "build/%s.sh" %(self.name())
                if os.path.isfile(script):
                    files += [script]
            except:
                pass
        files = dropDuplicates(files)
        files.sort()
        return(files)

    def setfiles(self,files):
        self.yml['files'] = files

    # Returns array of scripts
    def scripts(self):
        script = []
        if 'script' in self.yml:
            script = self.yml['script']
        script = toList(script)
        return(script)

    def setscripts(self, script):
        self.yml['script'] = script

    def conflicts(self):
        conflicts = []
        if 'name' in self.yml:
            # Use wildcard to avoid setting directory as conflict, which would
            # prevent loading any modulefiles located in subdirectories
            conflicts += [self.yml['name'] + "/*"]
        if 'conflicts' in self.yml:
            conflicts += self.yml['conflicts']
        if conflicts:
            conflicts = dropDuplicates(conflicts)
            conflicts.sort()
        return conflicts

    def setconflicts(self,conflicts):
        self.yml['conflicts'] = conflicts

    def binaries(self):
        binary = []
        if 'binary' in self.yml:
            try:
                binary = self.yml['binary']
            except:
                pass
        binary = toList(binary)
        return(binary)

    def defaultVersion(self):
        default = ""
        try:
            if self.yml['set_default'] != 0:
                default = self.id()
        except:
            pass
        return default

    # relative path to module's software
    def swPath(self):
        if self.path:
            return self.path
        else:
            return self.id()
