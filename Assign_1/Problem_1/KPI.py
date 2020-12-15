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
No_airports  = len(airports_lst)

ASK_lst = np.zeros((No_airports,No_airports))   # available seat kilometer 
RPK_lst = np.zeros((No_airports,No_airports))   # revenue passenger kilometer
LF_lst  = np.zeros((No_airports,No_airports))   # load factor

CASK_lst = np.zeros((No_airports,No_airports)) # Cost per ASK
RASK_lst = np.zeros((No_airports,No_airports)) # revenue per ASK
operatingProfit = np.zeros((No_airports,No_airports)) # operating profit

for i in range(No_airports):
    for j in range(No_airports):
        if i!=j:
            if z_ij.iloc[i, j + 1] != 0:
                origin = airports_lst[i]    # To check the current airport origin
                dest   = airports_lst[j]    # To check the current airport destination
                distance = funct.calculateDistance(origin, dest)
                gi = 1
                gj = 1
                if origin == 'Paris':
                    gi = 0
                if dest == 'Paris':
                    gj = 0

                direct_ij   = x_ij.iloc[i,j+1] 
                transfer_ij = 0
                revenue_w_ij= 0
                for airport in range(No_airports):  # add transfer passengers that have to first travel to paris to transfer there to their final destination
                    if i != airport:
                        origin_w = airports_lst[i]    # To check the current airport origin
                        dest_w   = airports_lst[airport]    # To check the current airport destination
                        distance_w_ij = funct.calculateDistance(i,airport)
                        
                        wij          = w_ij.iloc[i,airport+1]*(1-gj) + w_ij.iloc[airport,j+1]*(1-gi)
                        transfer_ij += wij
                        yield_w_ij   = 5.9 * distance_w_ij**(-0.76) + 0.043   
                        RPK_w_ij     = wij * distance
                        revenue_w_ij += yield_w_ij * RPK_w_ij

                yield_x_ij   = 5.9 * distance**(-0.76) + 0.043  # yield per RPK
                RPK_x_ij     = direct_ij * distance
                revenue_x_ij = yield_x_ij * RPK_x_ij

                total_pax = direct_ij + transfer_ij
                RPK_ij    = total_pax * distance
            
                # Single flight leg related costs
                zij  = ast.literal_eval(z_ij.iloc[i, j+1])
                ASK_ij = 0
                Cx_ij  = 0  # fixed operating cost
                Ct_ij  = 0  # time-dependent cost
                Cf_ij  = 0  # fuel cost
                for k in range(len(zij)):
                    ac_type = zij[k][0]
                    no_flights_ac = zij[k][1]
                    seats    = float(aircraftData.loc['Seats','Aircraft '+str(int(ac_type+1))])
                    ac_speed = float(aircraftData.loc['Speed','Aircraft '+str(int(ac_type+1))])
                    ASK_ij  += seats * distance * no_flights_ac

                    # Itinirary cost computations
                    cx_ij  = float(aircraftData.loc['Fixed operating cost','Aircraft '+str(int(ac_type+1))])
                    Cx_ij += cx_ij * no_flights_ac

                    ct_ij  = float(aircraftData.loc['Time cost parameter','Aircraft '+str(int(ac_type+1))])
                    Ct_ij += ct_ij * distance/ac_speed * no_flights_ac

                    cf_ij  = float(aircraftData.loc['Fuel cost parameter','Aircraft '+str(int(ac_type+1))])
                    Cf_ij += cf_ij * 1.42 / 1.5 * distance * no_flights_ac
                
                # weekly load factor on flight leg
                LF_ij = RPK_ij/ASK_ij

                # weekly operating cost on flight leg
                C_ij    = (Cx_ij + Ct_ij + Cf_ij) * (0.7+0.3*gi*gj)
                CASK_ij = C_ij / ASK_ij

                # revenue
                revenue_ij = revenue_x_ij + revenue_w_ij
                RASK_ij    = revenue_ij/ASK_ij

                operatingProfit_ij = revenue_x_ij + revenue_w_ij - ASK_ij * CASK_ij

                RPK_lst[i,j]  = RPK_ij
                ASK_lst[i,j]  = ASK_ij
                LF_lst[i,j]   = LF_ij
                CASK_lst[i,j] = CASK_ij
                RASK_lst[i,j] = RASK_ij
                operatingProfit[i,j] = operatingProfit_ij

# Total ac lease cost
Cl = 0
for ac in AC.iloc[:,0]:
    ac_type = int(ac[-1])
    leaseCost = aircraftData.loc['Weekly lease cost','Aircraft '+str(int(ac_type+1))] 
    no_flights_ac = float(AC.loc[ac_type,'Number of AC'])
    Cl += leaseCost * no_flights_ac

ASK  = pd.DataFrame(ASK_lst,columns=networkData['city'],index=networkData['city'])
RPK  = pd.DataFrame(RPK_lst,columns=networkData['city'],index=networkData['city'])
LF   = pd.DataFrame(LF_lst,columns=networkData['city'],index=networkData['city'])
CASK = pd.DataFrame(CASK_lst,columns=networkData['city'],index=networkData['city'])
RASK = pd.DataFrame(RASK_lst,columns=networkData['city'],index=networkData['city'])
OperProfit = pd.DataFrame(operatingProfit,columns=networkData['city'],index=networkData['city'])

totalProfit = sum(OperProfit.sum()) - Cl

print()