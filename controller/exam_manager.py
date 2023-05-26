from typing import List, Tuple, Union
import contextvars
from datetime import datetime, date, time, timezone
import time
from typing_extensions import Self

from model.exam import ComplementaryExamData
from model.hardware import InsolePackage
from model import examDB


examsInProgress = contextvars.ContextVar('insolesInUse')
examsInProgress.set({}) # examId -> complementaryExamData


class ExamManager:
    
    
    def __init__(self) -> None:
        try:
            self.examDatabase = examDB.ExamDB()
            print("BANCO DE DADOS IA CONECTADO!")
        except:
            print("ERRO AO CONECTAR BANCO DE DADOS IA!")

            
    def insertExamRegistries(self, examId: str, insolePackage: InsolePackage) -> None:
        registries = []
        for registry in insolePackage.leftData:
            registries.append([examId, insolePackage.leftInsoleId, *registry])

        for registry in insolePackage.rightData:
            registries.append([examId, insolePackage.rightInsoleId, *registry])

        self.examDatabase.insertExamRegistries(registries)

    def getExamByInsoleId(self, leftInsoleId: str, rightInsoleId: str) -> Tuple[Union[str, ComplementaryExamData, None]]:
        examsInProgress_ = examsInProgress.get()

        for examId, complementaryData in examsInProgress_.items():
            examLeftInsoleId = complementaryData.leftInsoleId
            examRightInsoleId = complementaryData.rightInsoleId
            #print(leftInsoleId,examLeftInsoleId,"----",rightInsoleId,examRightInsoleId)
            if leftInsoleId == examLeftInsoleId and rightInsoleId == examRightInsoleId:
                return (examId, complementaryData)

        return (None, None)

    def filterByTime(self, insolePackage: InsolePackage, startTime: str) -> InsolePackage:
        applyFilter = lambda registry: registry[-1] >= startTime
        print(insolePackage.leftData[-1])
        filteredLeftData = list(filter(applyFilter, insolePackage.leftData))
        filteredRightData = list(filter(applyFilter, insolePackage.rightData))

        filteredInsoleData = InsolePackage(leftInsoleId=insolePackage.leftInsoleId,
                                            rightInsoleId=insolePackage.rightInsoleId,
                                            leftData=filteredLeftData, rightData=filteredRightData)
        return filteredInsoleData

    def checkExamById(self, examId: str) -> bool:
        examsInProgress_ = examsInProgress.get()
        return examId in examsInProgress_.keys()

    def registerExam(self, examId: str, complementaryExamData: ComplementaryExamData) -> bool:
        examsInProgress_ = examsInProgress.get()

        if not examId in examsInProgress_.keys():
            examsInProgress_[examId] = complementaryExamData
            return True

        return False

    def _unregisterExam(self, examId: str) -> None:
        examsInProgress_ = examsInProgress.get()
        examsInProgress_.pop(examId)
        examData = self.examDatabase.deleteRegistriesByExamId(examId)
        return examData

    def cancelExam(self, examId: str) -> None:
        self._unregisterExam(examId)

    def concludeExam(self, examId: str) -> List[Tuple[Union[str, float]]]:
        examData = self._unregisterExam(examId)
        return examData

    def remove_expired(self, timeout: int):  #TIP: remove expired deixa exam_manager muito acoplado ao resto do programa. Talvez, remover de acordo com o examId seja melhor
        try:
            date_format_str = "%Y-%m-%d %H:%M:%S"
            examsInProgress = examsInProgress.get().copy()
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for examId, complementaryData in examsInProgress.items():
                start = (complementaryData.examStartTime)
                start = datetime.strptime(start, date_format_str)
                now =   datetime.strptime(str(now), date_format_str)
                diff = now - start.total_seconds()
                if diff > timeout:
                    self._unregisterExam(examId)
        except:  #TIP: não é uma boa prática deixar except geral, porque pode disfarçar bugs no programa
            pass


    def _relearnedModel(self):
        self.examDatabase.relearnedModel()
        return None