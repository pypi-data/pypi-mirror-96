import time
import grpc
import dataWorker_pb2 as statsModel
import dataWorker_pb2_grpc as stats
import datetime 
import threading
import pandas as pd
from google.protobuf.json_format import MessageToJson
import queue
import inspect
import numpy as np
from helper import log
import grpc
import asyncio
import simplejson as json
from WorkerJobProcess import WorkerJobProcess
from Registrar import Registrar
import zlib
from StatisticRuleJob import StatisticRuleJob

class StatisticsRuleWorker(WorkerJobProcess):

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

    def getIndicatorMethod(self, indicator):
        found_method = None
        registeredFunctions = self.registrar.statisticsCallbacks

        if "." + indicator.statisticFunction in registeredFunctions:
            found_method = registeredFunctions["." + indicator.statisticFunction]
        else:
            if indicator.statisticFunction in registeredFunctions is not None:
                found_method = registeredFunctions[indicator.statisticFunction]

        return found_method

    def onStatisticFunctionError(self, statisticJob, error):

        statsError = statsModel.StatisticRuleFunctionError()
        statsError.error.message = str(error)
        statsError.worker.CopyFrom(self.workerJob)
        statsError.statisticFunction.CopyFrom(statisticJob)

        self.statisticInterface.OnStatisticFunctionErrorOccured(statsError)

        return False

    def calculateStatisticFunction(self, statisticRule):

        try:
            targetMethod = self.getIndicatorMethod(statisticRule)

            message_as_json = json.loads(MessageToJson(statisticRule))
            log.info(message_as_json)
            inputs = message_as_json["inputs"]

            raw_inputs = self.extractInputsFromDataFrameAndInsertInDataFrame(inputs)
            inputs_with_raw_values = {}
            for k in inputs:
                inputs_with_raw_values[k] = inputs[k]["value"]
            statisticJob = StatisticRuleJob(self.getDf(), inputs_with_raw_values, statisticRule.id, self)

            if (inspect.iscoroutinefunction(targetMethod["process"])):
                async def runandwait():
                    result = await asyncio.wait(
                        [targetMethod["process"](raw_inputs, statisticJob)],
                        return_when=asyncio.FIRST_COMPLETED)

                loop = asyncio.new_event_loop()
                process = loop.run_until_complete(runandwait())
            else:
                process = targetMethod["process"](raw_inputs, statisticJob)
        except Exception as e:
            log.info("Error on Statistic")
            log.error(e)
            self.onStatisticFunctionError(statisticRule, e)
            pass

        return statisticJob.getResultColumns()

    def calculateRulesGroup(self, ruleGroup):

        if ruleGroup.enabled == False:
            return False

        allResults = []
        for r in ruleGroup.rules:
            try:
                if r.type == "group":
                    groupResults = self.calculateRulesGroup(r)
                    allResults.append(groupResults)
                else:
                    ruleResults = self.calculateStatisticFunction(r)
                    allResults.append(ruleResults)
            except Exception as e:
                log.error("Problem mit Indicator", str(e))
                pass

        combinator = ruleGroup.combinator

        if combinator == "and":
            resultColumn = np.logical_and.reduce(allResults)
        elif combinator == "or":
            resultColumn = np.logical_or.reduce(allResults)

        if ruleGroup.combinator_not == True:
            resultColumn = np.logical_not.reduce(resultColumn)

        self.getDf()["r_"+ruleGroup.id] = resultColumn

        return resultColumn
        
    def run(self):

        returnRow = False
        # lets fill teh dataframe with previous value because of the different merged timeframes
        self.dataFrame = self.dataFrame.fillna(method='ffill')
        try:

            returnRow = self.calculateRulesGroup(self.statisticConfig)
        except Exception as e:
            log.error("Problem mit Indicator", str(e))
            pass

        if not isinstance(returnRow, list) and not isinstance(returnRow, np.ndarray):
            returnRow = False

        self.getDf()["r_master"] = returnRow

        self.getDf()["r_master"] = self.getDf()["r_master"].astype(int)

        self.chipmunkDb.save_as_pandas(self.getDf().query("r_master > 0")[["r_master"]], self.chartConfigData.workspace_id,
                                  mode="dropbefore",
                                  domain="stats")

        partiallyData = statsModel.StatisticBulkedPartiallyData()
        resultData = statsModel.StatisticRulePartiallyData()
        resultData.resultName = "master"
        resultData.collectionid = ""
        resultData.worker.CopyFrom(self.workerJob)
        partiallyData.ruleData.CopyFrom(resultData)

        self.statisticInterface.OnStatisticPartiallyData(partiallyData)


        