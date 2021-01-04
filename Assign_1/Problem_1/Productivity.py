from formatFunctions import readOptimizedData
import demand
import demand_globalData as globals
import demand_functions as funct
import aircraft_loadData as aircraftLoad
import ast
import numpy as np
import pandas as pd

demand.demandForecast()
networkData = globals.networkData
aircraftData = aircraftLoad.loadData()
aircraft = range(len(aircraftData.columns))

x_ij, w_ij, z_ij, AC = readOptimizedData()

airports_lst = networkData['city'].to_numpy()
No_airports = len(airports_lst)

g = np.ones(len(airports_lst))
g[airports_lst=='Paris'] = 0

ASK_AC1 = 0
ASK_AC2 = 0
ASK_AC3 = 0
ut_AC1  = 0
ut_AC2  = 0
ut_AC3  = 0
d       = 0
dislis  = np.array([])

for i in range(No_airports):
    for j in range(No_airports):
        if i != j:
            if z_ij.iloc[i, j] != 0:
                origin = airports_lst[i]  # To check the current airport origin
                dest = airports_lst[j]    # To check the current airport destination
                distance = funct.calculateDistance(origin, dest)
                dislis = np.append(dislis, distance)
                #if distance <= 1500:
                #d += 1

                zij = ast.literal_eval(z_ij.iloc[i, j])
                for k in range(len(zij)):
                    ac_type = zij[k][0]
                    no_flights_ac = zij[k][1]
                    singleAircraftData = aircraftData.iloc[:, ac_type]

                    seats = singleAircraftData['Seats']
                    spk = singleAircraftData['Speed']  # speed of aircraft
                    TAT = singleAircraftData['Average TAT']/60

                    if ac_type == 0:
                        ASK_AC1 += seats * distance * no_flights_ac
                        ut_AC1 += (distance/spk + TAT*(1.5 - 0.5 * g[j]))*no_flights_ac

                    elif ac_type == 1:
                        ASK_AC2 += seats * distance * no_flights_ac
                        ut_AC2 += (distance/spk + TAT*(1.5 - 0.5 * g[j]))*no_flights_ac

                    elif ac_type == 2:
                        ut_AC3 += (distance/spk + TAT*(1.5 - 0.5 * g[j]))*no_flights_ac
                        ASK_AC3 += seats * distance * no_flights_ac
                        d += no_flights_ac
                    else :
                        print("Unknown AC")
                        break

print()
print(ASK_AC3+ASK_AC1+ASK_AC2, '     -> Same sum as ASK')
print()
print('Total utilization time: ', ut_AC3+ut_AC2+ut_AC1)
print('Max possible utilization time time: ', 8*70)
print('Utilisation p AC: ', 'AC 1', ut_AC1/3, 'AC 2', ut_AC2/1, 'AC 3', ut_AC3/4)
print()
print('Average distance: ', dislis.mean())
print('Max distance: ', dislis.max())
print('Min distance: ', dislis.min())


