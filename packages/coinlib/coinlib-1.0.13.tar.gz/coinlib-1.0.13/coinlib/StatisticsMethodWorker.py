import time
import grpc
import coinlib.dataWorker_pb2 as statsModel
import coinlib.dataWorker_pb2_grpc as stats
import datetime 
import threading
import pandas as pd
from google.protobuf.json_format import MessageToJson
import queue
import inspect
from coinlib.helper import log
import numpy as np
import grpc
import asyncio
import simplejson as json
from coinlib.WorkerJobProcess import WorkerJobProcess
from coinlib.Registrar import Registrar
import zlib
from coinlib.StatisticMethodJob import StatisticMethodJob

class StatisticsMethodWorker(WorkerJobProcess):

    def initialize(self):
        self.registrar = Registrar()
        self.statisticInterface = stats.StatisticsMethodWorkerStub(self.getChannel())
        if self.statisticConfig is None:
            self.statisticConfig = self.statisticInterface.GetConfig(self.workerJob)
        self.chartConfigData = self.statisticConfig.chartData
        pass

    def setConfig(self, configuration):
        self.statisticConfig = configuration
        pass

    def getMethodMethod(self, methodName):
        found_method = None
        registeredFunctions = self.registrar.statisticsCallbacks

        if "method_" + methodName in registeredFunctions:
            found_method = registeredFunctions["method_" + methodName]
        return found_method

    def onStatisticFunctionError(self, methodName, error):

        statsError = statsModel.StatisticMethodFunctionError()
        statsError.error.message = str(error)
        statsError.worker.CopyFrom(self.workerJob)

        self.statisticInterface.OnStatisticFunctionErrorOccured(statsError)

        return False

    def runMethodCallback(self, methodName, methodParams):

        try:
            targetMethod = self.getMethodMethod(methodName)

            if methodParams == "":
                methodParams = "{}"

            params_as_json = json.loads(methodParams)
            inputs = params_as_json
            raw_inputs = {}
            try:
                raw_inputs = self.extractInputsFromDataFrameAndInsertInDataFrame(inputs)
            except Exception as err:
                pass

            inputs_with_raw_values = {}
            for k in inputs:
                inputs_with_raw_values[k] = inputs[k]["value"]
            statisticJob = StatisticMethodJob(self.getDf(), inputs_with_raw_values, self)

            if inspect.iscoroutinefunction(targetMethod["process"]):
                async def runandwait():
                    result = await asyncio.wait(
                        [targetMethod["process"](raw_inputs, statisticJob)],
                        return_when=asyncio.FIRST_COMPLETED)

                loop = asyncio.new_event_loop()
                process = loop.run_until_complete(runandwait())
            else:
                process = targetMethod["process"](raw_inputs, statisticJob)
        except Exception as e:
            log.exception("Error on Statistic Method Running")
            log.error(e)
            self.onStatisticFunctionError(methodName, e)
            return []

        return statisticJob.getResultPlots()

    def runMethodForSingleWindow(self, configWithWindow):

        returnRows = self.runMethodCallback(configWithWindow.method, configWithWindow.params)

        ## returnRows
        # save the returnRows to chipmunk as a storage database

        workspace = self.chartConfigData.workspace_id
        windowid = configWithWindow.windowId

        self.chipmunkDb.save_document(workspace, windowid.replace("#", ""), returnRows)

        partiallyData = statsModel.StatisticBulkedPartiallyData()
        resultData = statsModel.StatisticMethodPartiallyData()
        resultData.method = configWithWindow.method
        resultData.documentId = "asdf"
        resultData.worker.CopyFrom(self.workerJob)
        resultData.windowId = configWithWindow.windowId

        partiallyData.methodData.CopyFrom(resultData)
        self.statisticInterface.OnStatisticPartiallyData(partiallyData)

        return True

    def run(self):

        # lets fill teh dataframe with previous value because of the different merged timeframes
        ##self.dataFrame.fillna(method='ffill')

        #workerList = []
        # iterate over all config method windows
        ##for config in self.statisticConfig.windows:
        #    t = threading.Thread(target=self.runMethodForSingleWindow, args=[config], daemon=True)
        #    workerList.append(t)

        #for w in workerList:
        #    w.start()

        ## wait for all threads finished
        #for w in workerList:
        #    try:
        #        w.join()
        #    except Exception as e:
        #        pass

        t = threading.Thread(target=self.runMethodForSingleWindow, args=[self.statisticConfig], daemon=True)

        t.start()

        try:
           t.join()
        except Exception as e:
           pass

        return True
        