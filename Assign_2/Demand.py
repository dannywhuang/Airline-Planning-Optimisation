import pandas as pd

class Demand:
    def __init__(self):
        self.data = pd.read_excel('data/demand.xlsx', index_col=0, usecols='A:AG',skiprows=[0,1,2,3])

