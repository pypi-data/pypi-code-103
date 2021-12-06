#!/usr/bin/env python3

import yaml
import sys
import os
import docker
import json

from .module import unameFields, INDENT
from .modules import *

from colorama import Fore, Back, Style

verbosity = False
force = False
modulesPrefix = '/usr/local/Modules'

def print_red(s):
    print(Fore.RED + s + Fore.WHITE)

def print_yellow(s):
    print(Fore.YELLOW+ s + Fore.WHITE)

DEBUG = 0

def modulefileHeader(module):
    header = "#%Module\n##\n"
    header += "## " + module.id() + "\n"
    header += "##\n"
    header += "set sysname    [uname sysname]\n"
    header += "set machine    [uname machine]\n"
    header += "set domain     [uname domain]\n"
    header += "set os_release [uname release]\n"
    header += "set os_version [uname version]\n"
    header += "set nodename   [uname nodename]\n"
    return header + "\n"

def modulefileHelp(module, indent):
    helpStr = indent + "proc ModulesHelp { } {\n"
    lines = module.help().split("\n")
    for i in range(0, len(lines)-1):
        line = lines[i].replace('"', '\\"')
        helpStr += indent + INDENT + "puts stderr \"" + line + "\"\n"

    # Footer
    helpStr += indent + INDENT + "puts stderr \"\"\n"
    helpStr += indent + INDENT + "puts stderr \"" + INDENT + "version: " + module.version() + "\"\n"
    if module.website():
        helpStr += indent + INDENT + "puts stderr \"" + INDENT + "website: " + module.website() + "\"\n"
    helpStr += indent + "}\n"
    return helpStr

def modulefileConflicts(module, indent):
    # always conflict with other versions of the same modules
    conflicts = module.conflicts()
    conflictStr = ""
    for c in conflicts:
        conflictStr += indent + "conflict " + c + "\n"
    return conflictStr

def modulefileDepends(module, indent):
    dependStr = ""
    for d in module.depends():
        dependStr += indent + "module load %s; prereq %s\n" % (d, d)
    return dependStr

def modulefileDependsNoUnload(module, indent):
    dependStr = ""
    for d in module.dependsSticky():
        dependStr += indent + "if {![is-loaded %s]} { module load %s }; prereq %s\n" % (d, d, d)
    return dependStr

# Set the prefix to the root of the module software
def swPrefix(module):
    prefix = "set prefix %s/sw/%s/%s\n" % (modulesPrefix, module.name(), module.version())
    return prefix

# Set the prefix to the root of the module software
# MODULES_PREFIX is set in the modules environment config
def modulefilePrefix(module, indent):
    # virtual envrionment modules don't need a sw prefix
    if module.type == "virtual":
        return ""
    # override definition
    if module.prefix():
        return indent + module.prefix() + "\n"
    else:
        return indent + swPrefix(module) + "\n"

def modulefileBody(module, indent):
    body = ""
    body += modulefileHelp(module, indent)
    body += modulefileConflicts(module, indent)
    body += modulefileDepends(module, indent)
    body += modulefileDependsNoUnload(module, indent)
    body += modulefilePrefix(module, indent)
    # Set the interior body from configuration
    if module.body:
        lines = module.body().split("\n")
        for i in range(0, len(lines)-1):
            body += indent + lines[i] + "\n"
    return body

def constructBody(modules, unameValues, unameFields, i, depth, prevModID, string):
    # string for every indentation
    indent = INDENT

    # stop condition, out of unameValues fields
    if (i >= len(unameFields)):
        return string

    field = unameFields[i];
    if DEBUG: print(depth*indent + "key: " + field)

    # TODO: doesn't work when no uname fields defined
    if (len(unameValues[field]) > 0):
        # Start switch block for unameValues field
        string += depth*indent + "switch -glob $" + field + " {\n"
        depth += 1

        # add all field values
        for value in unameValues[field]:
            # module's identified by their vield values
            thisModID = prevModID + value

            # check if there are any modules along this field path, or skip.
            # this prevents us from printing out blocks for fields that
            # no module is using
            path = 0
            for moduleID in modules.keys():
                if (thisModID == moduleID[0:len(thisModID)]):
                    path = 1
                    break;
            if (path == 0):
                continue

            # Start case block for unameValues field value
            string += depth*indent + value + " {\n"
            if DEBUG: print(depth*indent + "prevModID: " + thisModID)

            # Add matching module or descend to the next unameValues field
            if thisModID in modules:
                string += modulefileBody(modules[thisModID], (depth+1)*indent)
            else:
                if DEBUG: print(depth*indent + "descending to next unameValues field")
                string = constructBody(modules, unameValues, unameFields, i+1, depth+1, thisModID, string)

            # End case block for unameValues field value
            string += (depth)*indent + "}\n"

        # End switch block for unameValues field
        string += (depth-1)*indent + "}\n"
    else:
        # No unameValues field values, try the next unameValues field
        string = constructBody(modules, unameValues, unameFields, i+1, depth, prevModID, string)

    return string


def createModulefile(modules, moduleDir):
    try:
        rootModule = modules[0]
    except:
        print("Found no valid modules")
        sys.exit(1)

    # collect all the uname values
    unameValues = dict()
    for module in modules:
        for field in unameFields:
            if field in module.yml:
                if not field in unameValues:
                    unameValues[field] = []
                unameValues[field] = list(set(unameValues[field] + [module.yml[field]]))

    # set the active fields, adding default value for modules that don't
    # specify a value
    activeFields = []
    for field in unameFields:
        if field in unameValues:
            unameValues[field] += ["default"]
            activeFields.append(field)

    # Associate modules with their uname field values
    moduleID = dict()
    for module in modules:
        modID = ""
        for field in activeFields:
            if field in module.yml:
                modID += module.yml[field]
            else:
                modID += "default"
        moduleID[modID] = module
        #DEBUG
        if DEBUG: print(modID)
        #print (module)

    body = constructBody(moduleID, unameValues, activeFields, 0, 0, "", "")

    # Determine path to modulefile
    modulefileDir = moduleDir + "/modulefiles"
    modulefileDir += "/" + rootModule.name()
    modulefile = modulefileDir + "/" + rootModule.version()
    if DEBUG: print(modulefile)

    try:
        os.makedirs(modulefileDir)
    except FileExistsError:
        pass # do nothing
    f = open(modulefile, "w+")
    f.write(modulefileHeader(modules[0]))
    f.write(body)
    f.close()

def createVersionFile(modules, moduleDir):
    defaults = dict()
    for module in modules:
        if module.defaultVersion():
            if not module.name() in defaults:
                defaults[module.name()] = module.defaultVersion()
            else:
                print("WARNING: multiple defaults for %s set in config" % module.name())
    for name in defaults.keys():
        modulefileDir = "%s/%s" % (moduleDir, name)
        try:
            os.makedirs(modulefileDir)
        except FileExistsError:
            pass # do nothing
        versionFile = "%s/.version" % (modulefileDir)
        versionStr = "#%%Module##\nmodule-version %s default\n" %(defaults[name])
        print("Creating version file %s" % versionFile)
        f = open(versionFile, "w+")
        f.write(versionStr)
        f.close()

def writeDockerLogs(logs, logFile):
    with open(logFile, 'w') as out:
        for log in logs:
            try:
                out.write((log['stream']))
            except:
                pass

def buildModule(module, modulePath, moduleDir, modulesPrefix, os_name, os_vers):
    global verbosity
    client = docker.from_env()

    print("Building module %s/%s for %s:%s" %(module.name(), module.version(), os_name, os_vers))

    path = modulePath
    tag = "module_%s-%s-%s-%s" % (module.name(), module.version(), os_name, os_vers)
    dockerfile = "%s/%s" % (path, module.dockerfile())
    user = "%d:%d" % (os.getuid(), os.getgid())
    buildPath = os.path.abspath(moduleDir)
    buildLog = "%s/log/%s_docker-build.log" %(buildPath, tag)
    runLog = "%s/log/%s_docker-run.log" %(buildPath, tag)

    logs = []
    buildargs = dict()
    buildargs['MODULES_PREFIX'] = modulesPrefix
    buildargs['MODULE_NAME'] = module.name()
    buildargs['MODULE_VERS'] = module.version()
    buildargs['OS'] = os_name
    buildargs['OS_VERS'] = os_vers

    # make logfile dir
    try: os.makedirs("%s/log" % buildPath)
    except FileExistsError: pass

    if verbosity: print("  creating docker image %s" %(tag))
    try:
        (image, logs) = client.images.build(path=path, tag=tag, dockerfile=dockerfile, buildargs=buildargs)
        writeDockerLogs(logs, buildLog)
    except docker.errors.BuildError as error:
        print_red("  docker image build failed for module %s/%s: %s" %(module.name(), module.version(), error))
        # TODO logs are empty when build throws
        return False

    if verbosity: print("  running docker image %s" %(tag))
    try:
        try: os.makedirs(buildPath)
        except FileExistsError: pass
        logs = client.containers.run(image, volumes=["%s:%s" %(buildPath, modulesPrefix)], user=user)
        writeDockerLogs(logs, runLog)
    except docker.errors.ContainerError as error:
        print_red("  build failed for module %s/%s: %s" %(module.name(), module.version(), error))
        # TODO logs are empty when build throws
        return False

    return True

def build(config, path = "modules", prefix = "/usr/local/Modules", verbose = False, force = False, debug = False, target_os = "ubuntu:18.04") :
    global modulesPrefix

    modulesPrefix = prefix
    modules = getModules(config)
    moduleDir = os.path.abspath(path)
    modulePath = os.path.abspath(os.path.dirname(config))
    [os_name, os_vers] = target_os.split(":", 2)

    # Divide the modules up into their respective name/version
    modulesGroups = dict()
    for module in modules:
        group = module.id()
        if not group:
            print("empty group id")
            continue
        if not group in modulesGroups:
            modulesGroups[group] = []
        modulesGroups[group] += [module]

    # Spin off a single modulefile for each group
    for group in modulesGroups.keys():
        # do the build here
        for module in modulesGroups[group]:
            buildSucceeded = buildModule(module, modulePath, moduleDir, modulesPrefix, os_name, os_vers)
        if (buildSucceeded):
            print("Creating modulefile for %s" %(group))
            createModulefile(modulesGroups[group], moduleDir)
            createVersionFile(modules, moduleDir)
        else:
            print_yellow("skipping modulefile for %s" %(group))

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("module", help="modulefile config", type=str)
    parser.add_argument("-p", "--prefix", default="/usr/local/Modules",
                        help="modules prefix, the path to mount point")
    parser.add_argument("-o", "--output-dir", default="build",
                        help="build modules in output directory")
    parser.add_argument("-v", "--verbose",
                        help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-f", "--force",
                        help="force rebuild of docker images",
                        action="store_true")
    parser.add_argument("--os", help="target os name", default="ubuntu")
    parser.add_argument("--os-vers", help="target os version", default="16.04")
    args = parser.parse_args()
    yamlFile = args.module
    modulePath = os.path.dirname(os.path.abspath(yamlFile))
    moduleDir = args.output_dir
    modulesPrefix = args.prefix
    verbosity = args.verbose
    force = args.force
    os_name = args.os
    os_vers = args.os_vers
    build(config=yamlFile, path=moduleDir, prefix=modulesPrefix, verbose=verbosity, debug=DEBUG, force=force, target_os="%s:%s"%(os_name,os_vers))
