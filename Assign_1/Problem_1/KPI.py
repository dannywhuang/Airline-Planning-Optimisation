from formatFunctions import readOptimizedData
import demand
import demand_globalData as globals
import demand_functions as funct
import aircraft_loadData as aircraftLoad
import ast
import numpy as np

demand.demandForecast()
networkData = globals.networkData
aircraftData = aircraftLoad.loadData()
aircraft = range(len(aircraftData.columns))

s = {}
for k in aircraft:
    singleAircraftData = aircraftData.iloc[:, k]
    s[k] = singleAircraftData['Seats']

x_ij,w_ij,z_ij,AC = readOptimizedData()

ac_no  =  ast.literal_eval( z_ij.iloc[0,2])[1][1]

airports_lst = np.array(networkData['city'])
No_airports = len(airports_lst)


ask = np.zeros((No_airports,No_airports))
rsk = np.zeros((No_airports,No_airports))
LF  = np.zeros((No_airports,No_airports))

for i in range(No_airports):
    for j in range(No_airports):
        if i!=j:
            if z_ij.iloc[i, j + 1] != 0:
                origin = airports_lst[i]    # To check the current airport origin
                dest   = airports_lst[j]    # To check the current airport destination
                distance = funct.calculateDistance(origin, dest)

                total_pax = x_ij.iloc[i,j+1] + w_ij.iloc[i,j+1]
                rsk[i,j]  = total_pax*distance

                zij  = ast.literal_eval(z_ij.iloc[i, j+1])
                ask_ij = 0
                for k in range(len(zij)):
                    ac_type = zij[k][0]
                    no_ac   = zij[k][1]
                    seats   = s[ac_type]
                    ask_ij  = ask_ij + seats*distance*no_ac
                ask[i,j]    = ask_ij
                LF[i,j]     = rsk[i,j]/ask[i,j]