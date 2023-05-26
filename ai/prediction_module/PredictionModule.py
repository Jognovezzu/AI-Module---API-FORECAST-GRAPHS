
import pickle
from typing import Dict

import pandas as pd



class PredictionModule:
    
    def __init__(self, predictionModelPath: str) -> None:
        self._predictionModel = None

        self._loadPredictionModel(predictionModelPath)

    def _loadPredictionModel(self, filepath: str) -> None:
        with open(filepath, 'rb') as file:
            self._predictionModel = pickle.load(file)

    def predict(self, data: pd.DataFrame) -> Dict[str, int]:

        aiResult = self._predictionModel.predict(data)
        
        return aiResult
