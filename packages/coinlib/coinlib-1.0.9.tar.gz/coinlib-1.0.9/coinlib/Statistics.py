from coinlib.helper import getEnvironment
from coinlib.helper import get_current_kernel
import copy
import coinlib.dataWorker_pb2 as statsModel
import coinlib.dataWorker_pb2_grpc as stats
import json
from coinlib.helper import is_in_ipynb
from grpc._cython.cygrpc import CompressionAlgorithm
from grpc._cython.cygrpc import CompressionLevel
import grpc
import os
import ipynb_path
import sys
from coinlib.Registrar import Registrar
import inspect
from google.protobuf.json_format import MessageToDict


class Statistics:
    def __init__(self):
        self.registrar = Registrar()
        self.channel = self.createChannel()
        self.statisticsInterface = stats.StatisticsStub(self.channel)
        pass

    def createChannel(self):
        chan_ops = [('grpc.max_receive_message_length', 1000 * 1024 * 1024),
                    ('grpc.default_compression_algorithm', CompressionAlgorithm.gzip),
                    ('grpc.grpc.default_compression_level', CompressionLevel.high)]
        return grpc.insecure_channel(self.registrar.coinlib_backend, options=chan_ops,
                                     compression=grpc.Compression.Gzip)


    def registerStatisticsRuleFunction(self, process, identifier,
                                   name, description, inputs,
                                   group=""):
        type = "stats_function"

        registration = statsModel.StatisticRuleFunctionRegistration()
        registration.identifier = identifier
        registration.name = name
        registration.group = group
        registration.description = description

        registration.stage = getEnvironment()

        if not is_in_ipynb:
            namespace = sys._getframe(1).f_globals
            cwd = os.getcwd()
            rel_path = namespace['__file__']
            abs_path = os.path.join(cwd, rel_path)
            only_filename = os.path.splitext(os.path.basename(abs_path))[0]
            splitted = only_filename.split("_")
            only_filename_without_version = "_".join(splitted[:-1])

            registration.plugin = only_filename_without_version
            registration.pluginVersion = splitted[-1].replace("-", ".")
        else:
            abs_path = ipynb_path.get()
            only_filename = os.path.splitext(os.path.basename(abs_path))[0]

            registration.plugin = only_filename
            registration.pluginVersion = "?"

        for input in inputs:
            inputModel = statsModel.StatisticFunctionInputs()
            inputModel.type = input["type"]
            inputModel.identifier = input["identifier"]
            inputModel.label = input["label"]
            if "default" in input:
                inputModel.defaultValue = input["default"]
            registration.inputs.append(inputModel)


        registration_dict = MessageToDict(registration)

        # before we send the data, we need to add the "callback"
        # to a global handler list
        self.registrar.statisticsCallbacks[group + "." + identifier] = registration_dict
        self.registrar.statisticsCallbacks[group + "." + identifier]["process"] = process

        self.statisticsInterface.registerStatisticRuleFunction(registration)

        return True

    def registerStatisticMethod(self, process, identifier, name,
                                   description, inputs, refreshOn=[]):
        type = "stats_method"

        registration = statsModel.StatisticMethodRegistration()
        registration.identifier = identifier
        registration.name = name
        for r in refreshOn:
            registration.refreshOn.append(r)
        registration.description = description
        registration.stage = getEnvironment()


        if not is_in_ipynb:
            namespace = sys._getframe(1).f_globals
            cwd = os.getcwd()
            rel_path = namespace['__file__']
            abs_path = os.path.join(cwd, rel_path)
            only_filename = os.path.splitext(os.path.basename(abs_path))[0]
            splitted = only_filename.split("_")
            only_filename_without_version = "_".join(splitted[:-1])

            registration.plugin = only_filename_without_version
            registration.pluginVersion = splitted[-1].replace("-", ".")
        else:
            abs_path = ipynb_path.get()
            only_filename = os.path.splitext(os.path.basename(abs_path))[0]

            registration.plugin = only_filename
            registration.pluginVersion = "?"

        for input in inputs:
            inputModel = statsModel.StatisticMethodInputs()
            inputModel.type = input["type"]
            inputModel.identifier = input["identifier"]
            inputModel.label = input["label"]
            if "values" in input:
                inputModel.values = json.dumps(input["values"])
            if "default" in input:
                inputModel.defaultValue = input["default"]
            if "defaultValue" in input:
                inputModel.defaultValue = input["defaultValue"]
            registration.inputs.append(inputModel)


        registration_dict = MessageToDict(registration)

        # before we send the data, we need to add the "callback"
        # to a global handler list
        self.registrar.statisticsCallbacks["method_"+identifier] = registration_dict
        self.registrar.statisticsCallbacks["method_"+identifier]["process"] = process

        self.statisticsInterface.registerStatisticMethod(registration)

        return True