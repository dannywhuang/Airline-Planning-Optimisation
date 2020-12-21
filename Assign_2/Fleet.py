import pandas as pd
from Aircraft import Aircraft

class Fleet:
    def __init__(self):
        self.data = pd.read_excel('data/fleet.xlsx', index_col=0, usecols='A:D')
        self.amount = {}
        self.aircraftList = {}
        for i in self.data.columns:
            fl = self.data[i]
            self.amount[i] = fl['Fleet']
            self.aircraftList[i] = Aircraft(i, fl['Speed'], fl['Cargo capacity'], fl['Average TAT'], fl['Maximum Range'], fl['Runway Required'], fl['Lease Cost'], fl['Fixed Operating Cost'], fl['Cost per Hour'], fl['Fuel Cost Parameter'])

