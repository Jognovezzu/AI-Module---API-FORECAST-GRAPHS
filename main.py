from shutil import ReadError
import requests as req
from sqlalchemy import null
import traceback
#from os import sync
from ai.AiModule import AiModule
from datetime import datetime
import controller.exam_manager as exam_manager

from model.api import BasicResponse, DiagnosticResponse
from model.exam import ComplementaryExamData, ExamConclusion
from model.exam.doctor_recommendation import Doctor_recommendation
from model.hardware import InsolePackage
import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi_utils.tasks import repeat_every
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Server settings
HOST = '0.0.0.0'
PORT = 8000

EXAM_TIMEOUT_IN_SECONDS = 900
RELEARNED_TIME = 7884000


# AI settings
#AI_MODEL_FILEPATH = './ai/model.pk1'
AI_MODEL_FILEPATH = './ai/Model_ClusterRF.pk1'
#'./ai-api/ai/model.pk1'

app = fastapi.FastAPI()
aiModule = AiModule(AI_MODEL_FILEPATH)

app.add_middleware(CORSMiddleware, 
                    allow_origins = ["*"],
                    allow_methods = ["*"],
                    allow_headers = ["*"]
                    )


examManager = exam_manager.ExamManager()

@app.on_event('startup')
@repeat_every(seconds=EXAM_TIMEOUT_IN_SECONDS,wait_first=True) 
def task_remove():
    examManager.remove_expired(EXAM_TIMEOUT_IN_SECONDS)


@repeat_every(seconds=RELEARNED_TIME,wait_first= True)
def start_relearned():
    examManager._relearnedModel()



@app.post('/ai-module', status_code=201)
async def insertHardwareData(insolePackage: InsolePackage):  #endpoint to receive data from hardware
    print("PACKAGE RECEIVED")
    examId, complExamData = examManager.getExamByInsoleId(insolePackage.leftInsoleId, insolePackage.rightInsoleId)
    
    if examId is not None:
        examStartTime = complExamData.examStartTime
        #print(examStartTime,"+++++++")
        filteredInsolePackage = examManager.filterByTime(insolePackage, examStartTime)
        examManager.insertExamRegistries(examId, filteredInsolePackage)

    #print(examId)
    return BasicResponse(message='Package has been received')

@app.patch('/ai-module/exams/{examId}/start')
async def startExam(examId: str, examData: ComplementaryExamData):
    #ExamId:
    #ComplementaryExamData: leftInsoleId: str
    #                       rightInsoleId: str
    #                       examStartTime: str
    datetime_str = str(datetime.now())
    datetime_str = datetime_str.replace('.',' ')[0:19]
    examData.examStartTime = examData.examStartTime.replace('T',' ')
    examData.examStartTime = examData.examStartTime[0:19]
    examData.examStartTime = datetime_str
    examInProgress = examManager.checkExamById(examId)
    #Check exam started is in Dict: exam_in_progress
    if examInProgress:
        return BasicResponse(message='The exam given is already in progress')
    #or started a new Exam and append in Dict: exam_in_progress
    else:
        examManager.registerExam(examId, examData)

    return BasicResponse(message='New exam started')

@app.patch('/ai-module/exams/{examId}/finish')

async def finishExam(examId: str):

    examInProgress = examManager.checkExamById(examId)
    #Check if examId is in Dict: Exam_in_Progress
    #print(exam_manager.examsInProgress)
    
    if not examInProgress:
        return DiagnosticResponse(message='The exam given is not in progress')
    else:
        examData = examManager.concludeExam(examId)
        aiResult = aiModule.run(examData,examId) 
        
        #Check if the Data is enough to make predictions
        if not aiResult.isValid:
            await aiModule._backconclusion(examId,None,0)


            
            return DiagnosticResponse(
                    message='There are not enough data to make predictions',
                    status=False
                    )
        else:
            #Call the module of Predict and return > GaitType and Graphs
            aiModule.saveResult(examId, aiResult)
            print("SALVO DADOS GRAFICOS_________________")
            #aiModule.saveResult1(examId, aiResult)
            await aiModule._backconclusion(examId,conclusion=aiResult.gaitType,enough=True)
            print("RECOMENDAÇÃO DO EXAME:",examId,"-->",aiResult.gaitType)
            print("ENVIADO PARA SERVIDOR_________________")
    
            return DiagnosticResponse(
                    message='The new exam was successfully completed',
                    status=True,
                    gaitType=aiResult.gaitType,
                    graphs=aiResult.graphs
                    )



@app.get('/ai-module/exams/{examId}/result')  # TIP: /ai-module/exams/{examId}/result parece mais intuitivo
async def consultExam(examId : str):
    examResult = aiModule.consultResult(examId)
    if examResult is None:
        return DiagnosticResponse(
                message='There is no data for the exam consulted'
                )
    else:
        return DiagnosticResponse(
                message='The consult was succesfully completed',
                gaitType=examResult['gaitType'],
                graphs=examResult['graphs']
                )

@app.get('/ai-module/exams/{examId}/result1')  # USING SQLITE TO CONSULT
async def consultExam(examId : str):
    examResult = aiModule.consultResult1(examId)
    if examResult is None:
        return DiagnosticResponse(
                message='There is no data for the exam consulted'
                )
    else:
        return DiagnosticResponse(
                message='The consult was succesfully completed',
                gaitType=examResult['gaitType'],
                graphs=examResult['graphs']
                )


@app.patch('/ai-module/exams/{examId}/doctor_recommendation')
async def update_recommendation(examId:str, doctor_recommendation:Doctor_recommendation):
    try:
        aiModule.update_final_recommendation(examId, doctor_recommendation.recommendation)
    except:
        print("ERROR PATCH UPADTE RECOMMENDATION")


if __name__ == '__main__':
    uvicorn.run(app, host=HOST, port=PORT )
