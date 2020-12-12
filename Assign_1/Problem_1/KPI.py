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

s = {}
for k in aircraft:
    singleAircraftData = aircraftData.iloc[:, k]
    s[k] = singleAircraftData['Seats']

x_ij,w_ij,z_ij,AC = readOptimizedData()

ac_no  =  ast.literal_eval( z_ij.iloc[0,2])[1][1]

airports_lst = np.array(networkData['city'])
No_airports = len(airports_lst)


ask = np.zeros((No_airports,No_airports))   # available seat kilometer 
rpk = np.zeros((No_airports,No_airports))   # revenue passenger kilometer
lf  = np.zeros((No_airports,No_airports))   # load factor

# compute operating costs, which consists of 1. Fixed operating costs (Cx), 2. Time-based costs (Ct), 3. Fuel costs (Cf)
Cx = np.zeros((No_airports,No_airports))
Ct = np.zeros((No_airports,No_airports))
Cf = np.zeros((No_airports,No_airports))
cask = np.zeros((No_airports,No_airports)) # Cost per ASK
rask = np.zeros((No_airports,No_airports)) # revenue per ASK
operatingProfit = np.zeros((No_airports,No_airports)) # operating profit

for i in range(No_airports):
    for j in range(No_airports):
        if i!=j:
            if z_ij.iloc[i, j + 1] != 0:
                origin = airports_lst[i]    # To check the current airport origin
                dest   = airports_lst[j]    # To check the current airport destination
                distance = funct.calculateDistance(origin, dest)

                total_pax = x_ij.iloc[i,j+1] + w_ij.iloc[i,j+1]
                rpk_ij    = total_pax * distance
                rpk[i,j]  = rpk_ij

                zij  = ast.literal_eval(z_ij.iloc[i, j+1])
                ask_ij = 0
                Cx_ij  = 0  # fixed operating cost
                Ct_ij  = 0  # time-dependent cost
                Cf_ij  = 0  # fuel cost
                for k in range(len(zij)):
                    ac_type = zij[k][0]
                    no_ac   = zij[k][1]
                    seats   = aircraftData.loc['Seats','Aircraft '+str(int(ac_type+1))]
                    ac_speed = aircraftData.loc['Speed','Aircraft '+str(int(ac_type+1))]
                    ask_ij  += seats * distance * no_ac

                    # Itinirary cost computations
                    Cx_ij += aircraftData.loc['Fixed operating cost','Aircraft '+str(int(ac_type+1))] * no_ac
                    Ct_ij += aircraftData.loc['Time cost parameter','Aircraft '+str(int(ac_type+1))] * distance/ac_speed * no_ac
                    Cf_ij += aircraftData.loc['Fuel cost parameter','Aircraft '+str(int(ac_type+1))] * 1.42 / 1.5 * distance * no_ac

                ask[i,j]    = ask_ij
                lf[i,j]     = rpk[i,j]/ask[i,j]

                # itinerary cost
                C_ij = Cx_ij + Ct_ij + Cf_ij
                CASK_ij = C_ij / ask_ij

                Cx[i,j] = Cx_ij
                Ct[i,j] = Ct_ij
                Cf[i,j] = Cf_ij
                cask[i,j] = CASK_ij

                # revenue
                yield_ij = (5.9 * distance**(-0.76) + 0.043)
                revenue_ij = yield_ij * rpk_ij
                rask_ij = revenue_ij/ask_ij
                rask[i,j] = rask_ij

                operatingProfit_ij = rpk_ij * yield_ij - ask_ij * CASK_ij
                operatingProfit[i,j] = operatingProfit_ij


# # Total ac lease cost
# for ac in AC.iloc[:,0]:
#     ac_type = int(ac[-1])
#     leaseCost = aircraftData.loc['Weekly lease cost','Aircraft '+str(int(ac_type+1))] 
#     no_ac = AC.loc[ac_type,'Number of AC']
#     Cl = leaseCost * no_ac
#     print()

ASK  = pd.DataFrame(ask,columns=networkData['city'],index=networkData['city'])
RPK  = pd.DataFrame(rpk,columns=networkData['city'],index=networkData['city'])
LF   = pd.DataFrame(lf,columns=networkData['city'],index=networkData['city'])
CASK = pd.DataFrame(cask,columns=networkData['city'],index=networkData['city'])
RASK = pd.DataFrame(rask,columns=networkData['city'],index=networkData['city'])
OperProfit = pd.DataFrame(operatingProfit,columns=networkData['city'],index=networkData['city'])

print()