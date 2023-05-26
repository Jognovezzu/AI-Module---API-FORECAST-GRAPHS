from typing import Dict, List, Union, Tuple
import json
from unittest import result
from xmlrpc.client import Boolean
import requests
import pandas as pd
import collections

from .ai_result import AiResult
from .graph_module import GraphModule
from .prediction_module import PredictionModule
from model import examDB

class AiModule:

    def __init__(self, modelFilepath: str) -> None:
        self._predictionModule = PredictionModule(modelFilepath)
    
        self.Database = examDB.ExamDB()
    
    def _hasEnoughData(self, data: pd.DataFrame) -> bool:
        MINIMUM_QUANTITY = 100
        print(len(data))
        return len(data) >= MINIMUM_QUANTITY  # NOTE: generic rule to validate the quantity of data. Don't forget to change it later

    def _preprocess(self, inputData: List[Tuple[Union[str, float]]]) -> pd.DataFrame:
        data = pd.DataFrame(inputData)
        #data.to_csv('example.csv')
        piezoelectricData = data

        #inertialData = data.iloc[:, 10:]
        piezoelectricData.rename(columns = { '0':'s1','1':'s2','2':'s3','3':'s4','4':'s5','5':'s6','6':'s7','7':'s8','8':'s9'}, inplace = True)

        # NOTE: if you need to preprocess the data, do it here!
        #
        return piezoelectricData
      

    @staticmethod
    def saveResult(examId: str, aiResult: AiResult) -> None:
        EXAM_RESULTS_PATH = './ai/exams_comp'
        with open(f'{EXAM_RESULTS_PATH}/{examId}.json', 'w') as file: 
            json.dump(aiResult.toDict(), file) 


    @staticmethod
    def consultResult(examId: str) -> Union[AiResult, None]:
        EXAM_RESULTS_PATH = './ai/exams_comp'

        try:
            with open(f'{EXAM_RESULTS_PATH}/{examId}.json', 'r') as file:
                
                aiResultDict = json.load(file)
                return aiResultDict
        except FileNotFoundError:
            return None

    def saveResult1(self,examId:str, aiResult: AiResult) -> None:
        self.Database.insertRecommendationData(examId,aiResult)

    def consultResult1(self,examId: str) -> Union[AiResult, None]:
         return self.Database.consultRecommendationData(examId)



    def run(self, inputData: List[Tuple[Union[str, float]]], examId:str) -> AiResult:
        if not self._hasEnoughData(inputData):
            return AiResult(isValid=False)

        piezoelectricData= self._preprocess(inputData)
        predictionResults = self._predictionModule.predict(piezoelectricData)
        result = collections.Counter(predictionResults).most_common()
        predictedClass = result[0][0] # get the most frequent class

 

        sensorsGraphsData = GraphModule.createSensorsGraphsData(piezoelectricData)
        predictionGraphsData = GraphModule.createPredictionGraphsData(predictionResults)
        graphsData = {**sensorsGraphsData, **predictionGraphsData}
        #print(graphsData)
        piezoelectricData["RECOMMENDATION_IA"] = predictionResults
        piezoelectricData["FINAL_RECOMMENDATION"] = None
        #piezoelectricData = pd.DataFrame
        piezoelectricData.insert(0,"examId",examId)

        print(piezoelectricData)
        
        self.Database.insertRelearnedData(piezoelectricData)



        return AiResult(gaitType=predictedClass, graphs=graphsData, isValid=True)


    def update_final_recommendation(self, examId: str, recommendation: str):
        self.Database.insert_final_rec(examId, recommendation)


    @staticmethod
    async def _backconclusion(examId: str, conclusion:str, enough:bool) ->None:
        try:
            ENDPOINT_BACK = "http://127.0.0.1:8081/conclusion/"
            data = ({"conclusion": conclusion,"enough": enough})
            requests.put(f'{ENDPOINT_BACK}{examId}', json= data)
        except:
            print("REQUEST TO SEND SERVER FAILED")