import pandas as pd

class Demand:
    def __init__(self, fileName):
        self.data = pd.read_excel('data/' + fileName, index_col=0, usecols='A:AG',skiprows=[0,1,2,3])

