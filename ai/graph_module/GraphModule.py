from typing import Any, Dict, List
from matplotlib.container import BarContainer

import pandas as pd
import numpy as np


BARCHART_ID = 'barchart'
LINECHART_ID = 'linechart'
PIECHART_ID = 'piechart'
PRESSURE_DISTRIBUTION_ID = 'pressure_distribution'

def createSensorsGraphsData(data: pd.DataFrame) -> Dict[str, Any]:
    return {
        LINECHART_ID: _createLinechart(data),
        BARCHART_ID: _createBarchart(data),
        PRESSURE_DISTRIBUTION_ID: _createPressureDistribution(data)
    }

def createPredictionGraphsData(data: Dict[str, float]) -> Dict[str, Any]:
    return {
        PIECHART_ID: _createPiechart(data),
        
    }

def _createBarchart(data: Dict[str, float]) -> Dict[str, float]:
    
    '''Returns percentage converted to decimal of each class'''
    data.rename(columns = { '0':'s1','1':'s2','2':'s3','3':'s4','4':'s5','5':'s6','6':'s7','7':'s8','8':'s9'}, inplace = True)
    print(data)

    barchartData = data.mean().div(3.33).round(2).to_dict()
    """barchartData['s1'] = barchartData.pop('0')
    barchartData['s2'] = barchartData.pop('1')
    barchartData['s3'] = barchartData.pop('2')
    barchartData['s4'] = barchartData.pop('3')
    barchartData['s5'] = barchartData.pop('4')
    barchartData['s6'] = barchartData.pop('5')
    barchartData['s7'] = barchartData.pop('6')
    barchartData['s8'] = barchartData.pop('7')
    barchartData['s9'] = barchartData.pop('8')"""

    return barchartData

def _createPiechart(data: Dict[str, float]) -> Dict[str, float]:
    '''Returns percentage of each prediction class'''
    unique, counts = np.unique(data, return_counts=True)
    piechartData = dict(zip(unique, ((counts/len(data))*100).round(2)))
    piechartData['Neutro'] = piechartData.pop('neutro')
    piechartData['Pronado'] = piechartData.pop('pronado')
    piechartData['Supinado'] = piechartData.pop('supinado')
    return piechartData

def _createLinechart(data: pd.DataFrame) -> Dict:

    '''Returns ativation of each sensor over time'''
    linechart = []
    for i in range (0,len(data),len(data)//10):
        x = data.iloc[i:i+len(data)//10].sum().div(len(data)//10).round(2).values
        temp = {}
        for j in range(0,len(x)):
            temp["s"+str(j+1)] = x[j]
        linechart.append(temp)

        #return a list of dict with the activation. (ex.: [{'s1':2.0,'s2'......},{'s1':1.6,'s2'......}])

    return linechart


def _createPressureDistribution(data: pd.DataFrame) -> List[float]:
    '''Returns ativation percentage of each sensor'''
    data.rename(columns = { '0':'s1','1':'s2','2':'s3','3':'s4','4':'s5','5':'s6','6':'s7','7':'s8','8':'s9'}, inplace = True)


    LEFT_ID = 'leftside'
    RIGHT_ID = 'rightside'
    SENSORS_ID = ('s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9')
    insolemap = {}
    right = data.sum().div(len(data)).div(3.33).to_dict()
    """right['s1'] = right.pop('0')
    right['s2'] = right.pop('1')
    right['s3'] = right.pop('2')
    right['s4'] = right.pop('3')
    right['s5'] = right.pop('4')
    right['s6'] = right.pop('5')
    right['s7'] = right.pop('6')
    right['s8'] = right.pop('7')
    right['s9'] = right.pop('8')"""
    insolemap[LEFT_ID]= right
    left = data.sum().div(len(data)).div(3.33).to_dict()
    """left['s1'] = left.pop('0')
    left['s2'] = left.pop('1')
    left['s3'] = left.pop('2')
    left['s4'] = left.pop('3')
    left['s5'] = left.pop('4')
    left['s6'] = left.pop('5')
    left['s7'] = left.pop('6')
    left['s8'] = left.pop('7')
    left['s9'] = left.pop('8')"""
    insolemap[RIGHT_ID]= x = left
    ### How should the Pressure Distribution Map work? (Mean? Mode? Median? Another?)

    return insolemap