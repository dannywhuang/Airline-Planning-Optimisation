import pandas as pd
import numpy as np

def loadData():
    # ====================
    # Load data from excel
    # ====================

    excelFileName_1 = 'aircraft_data'

    # Load aircraft data
    aircraftData_excel = pd.read_excel(excelFileName_1 + '.xlsx', usecols = 'B:F', skiprows = 1, index_col = 0)

    return aircraftData_excel

