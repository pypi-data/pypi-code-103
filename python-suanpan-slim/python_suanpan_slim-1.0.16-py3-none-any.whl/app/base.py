# coding=utf-8
from __future__ import absolute_import, print_function

import os
import json
import base64
import traceback
from suanpan.g import g
from suanpan.log import logger
from suanpan.base import Context
from suanpan.stream import stream
from suanpan.arguments import suanpanTypes


class APP:
    def __init__(self):
        self.func = None
        self.afterInitFunc = None
        nodeinfo = self.loadNodeInfo()
        self.inputArgs = self.addArguments(
            self.parseNodeInfo("inputs", nodeinfo))
        self.outputArgs = self.addArguments(
            self.parseNodeInfo("outputs", nodeinfo))
        self.paramArgs = self.addArguments(
            self.parseNodeInfo("params", nodeinfo))

    def parseNodeInfo(self, type, nodeinfo):
        data = {}
        for k, v in nodeinfo[type].items():
            data.update({
                k: {
                    "type": v["subtype"] if v.get("subtype") else v["type"],
                    "uuid": v["uuid"]
                }
            })
        return data

    def loadNodeInfo(self):
        nodeInfoBase64 = g.nodeInfo
        nodeInfoString = base64.b64decode(nodeInfoBase64).decode()
        nodeInfo = json.loads(nodeInfoString)
        return nodeInfo

    def __call__(self, func):
        self.func = func if func else self.func

    def afterInit(self, func):
        self.afterInitFunc = func if func else self.afterInitFunc

    def start(self, *args, **kwargs):
        logger.info("Start Running...")
        try:
            self.paramContext = self.loadParams(g)
            if self.afterInitFunc:
                self.afterInitFunc(Context(args=self.paramContext))
        except Exception as e:
            tracebackInfo = traceback.format_exc()
            logger.error(
                f"Load parameters or Run afterinit function error: {tracebackInfo}"
            )
            os._exit(0)
        for context in stream.subscribeMessage():
            try:
                inputContext = self.loadInputs(context)
                context.args.update({**self.paramContext, **inputContext})
                result = self.func(context)
                if result is not None:
                    self.send(result, context)
                logger.debug("Finshed, Waiting for Next Round...")
            except Exception as e:
                tracebackInfo = traceback.format_exc()
                logger.error(
                    f"Load input or Run main function error: {tracebackInfo}")
                continue

    def addArguments(self, configs):
        arguments = {}
        for key, value in configs.items():
            arguments.update({
                key:
                suanpanTypes[value["type"]](key=key, alias=value["uuid"])
            })
        return arguments

    def loadParams(self, context):
        logger.debug("Loading Param Arguments:")
        params = {}
        for k, v in context.items():
            if k in self.paramArgs.keys():
                params.update(self.paramArgs[k].load(v))
        return params

    def loadInputs(self, context):
        logger.debug("Loading Input Arguments:")
        params = {}
        for k, v in context.items():
            if k.startswith("in") and k[-1].isdigit():
                params.update(self.inputArgs[k.replace("in",
                                                       "inputData")].load(v))
        return params

    def saveOutputs(self, context):
        logger.debug("Saving Output Arguments:")
        params = {}
        for k, v in context.items():
            if k.startswith("out") and k[-1].isdigit():
                result = self.outputArgs[k.replace("out",
                                                   "outputData")].dump(v)
                for port, value in list(result.items()):
                    if port.startswith("out"):
                        port = port.replace(
                            "outputData",
                            "out") if port.startswith("outputData") else port
                        result[port] = value
                    else:
                        del result[port]
                params.update(result)
        return params

    def formatOutput(self, result):
        data = {}
        if isinstance(result, tuple):
            for i, d in enumerate(result):
                if d:
                    data.update({f"out{i+1}": d})
        else:
            data.update({"out1": result})
        return data

    def send(self, result, context):
        result = self.formatOutput(result)
        result = self.saveOutputs(result)
        logger.debug("Sending Result to Next Nodes...")
        stream.sendMessage(result, context)

    def contextGen(self):
        return stream.generateMessage()

    def sendWithoutContext(self, result):
        context = self.contextGen()
        self.send(result, context)

    def input(self, args):
        if not args.alias:
            args.alias = args.key.replace("inputData", "in")
        self.inputArgs.update({args.key: args})
        return self

    def param(self, args):
        self.paramArgs.update({args.key: args})
        return self

    def output(self, args):
        if not args.alias:
            args.alias = args.key.replace("outputData", "out")
        self.outputArgs.update({args.key: args})
        return self


app = APP()
