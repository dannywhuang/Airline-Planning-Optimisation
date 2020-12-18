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



No_acType_flight = np.array([182, 44, 162])
leasCost_acType  = np.array([45000, 34000, 320000])
avgCost_flight   = leasCost_acType/No_acType_flight
dist_acType = [0,0,0]
dist_acType = np.array([65266.09023764141, 33721.224188674685, 126699.88394319483])
avgCost_flight = leasCost_acType/dist_acType

# Total ac lease cost
Cl = 0
for ac in AC.iloc[:,0]:
    ac_type = int(ac[-1])
    leaseCost = aircraftData.loc['Weekly lease cost','Aircraft '+str(int(ac_type+1))] 
    no_flights_ac = float(AC.loc[ac_type,'Number of AC'])
    # leasCost_acType[ac_type] += leaseCost * no_flights_ac
    Cl += leaseCost * no_flights_ac




for i in range(No_airports):
    for j in range(No_airports):
        if i!=j:
            if z_ij.iloc[i, j] != 0:
                origin = airports_lst[i]    # To check the current airport origin
                dest   = airports_lst[j]    # To check the current airport destination
                distance = funct.calculateDistance(origin, dest)
                gi = 1
                gj = 1
                if origin == 'Paris':
                    gi = 0
                if dest == 'Paris':
                    gj = 0

                direct_ij   = x_ij.iloc[i,j] 
                transfer_ij = 0
                revenue_w_ij= 0
                for airport in range(No_airports):  # add transfer passengers that have to first travel to paris to transfer there to their final destination
                    airport_name = airports_lst[airport]
                    wij          = w_ij.iloc[i,airport]*(1-gj) + w_ij.iloc[airport,j]*(1-gi)    # check if there are any transfer passengers

                    if wij != 0:
                        if gj == 0:
                            origin_w = airports_lst[i]          # To check the current airport origin
                            dest_w   = airports_lst[airport]    # To check the current airport destination
                        elif gi == 0:
                            origin_w = airports_lst[airport]    # To check the current airport origin
                            dest_w   = airports_lst[j]          # To check the current airport destination

                        distance_w         = funct.calculateDistance(origin_w,dest_w)
                        distance_w_flight1 = funct.calculateDistance(origin_w,'Paris')
                        distance_w_flight2 = funct.calculateDistance('Paris',dest_w)

                        RPK_w_flight1 = wij * distance_w_flight1
                        RPK_w_flight2 = wij * distance_w_flight2
                        RPK_w_ij      = wij * distance_w

                        yield_w_ij    = 5.9 * distance_w ** (-0.76) + 0.043
                        rev_w_ij      = yield_w_ij * RPK_w_ij

                        distFrac = distance_w_flight1/distance_w_flight2
                        yield_w_flight1 = distFrac * RPK_w_ij/RPK_w_flight2 * yield_w_ij / (1 + distFrac * RPK_w_flight1/RPK_w_flight2)
                        yield_w_flight2 = yield_w_flight1/distFrac

                        transfer_ij += wij

                        revenue_w_ij += yield_w_flight1 * RPK_w_flight1*(1-gj) + yield_w_flight2 * RPK_w_flight2*(1-gi)

                yield_x_ij   = 5.9 * distance**(-0.76) + 0.043  # yield per RPK
                RPK_x_ij     = direct_ij * distance
                revenue_x_ij = yield_x_ij * RPK_x_ij

                total_pax = direct_ij + transfer_ij
                RPK_ij    = total_pax * distance
            
                # Single flight leg related costs
                zij  = ast.literal_eval(z_ij.iloc[i, j])
                ASK_ij = 0
                Cx_ij  = 0  # fixed operating cost
                Ct_ij  = 0  # time-dependent cost
                Cf_ij  = 0  # fuel cost
                leaseCost = 0
                
                for k in range(len(zij)):
                    
                    ac_type = zij[k][0]
                    no_flights_ac = zij[k][1]
                    singleAircraftData = aircraftData.iloc[:, ac_type]

                    # No_acType_flight[ac_type] += no_flights_ac

                    seats    = float(aircraftData.loc['Seats','Aircraft '+str(int(ac_type+1))])
                    spk = singleAircraftData['Speed']  # speed of aircraft
                    ASK_ij  += seats * distance * no_flights_ac

                    # Itinirary cost computations
                    CXk = singleAircraftData['Fixed operating cost']
                    Cx_ij += CXk * no_flights_ac

                    cTk = singleAircraftData['Time cost parameter']  # time based costs
                    Ct_ij += cTk * distance/spk * no_flights_ac

                    cfk = singleAircraftData['Fuel cost parameter']  # fuel cost
                    Cf_ij += cfk * 1.42 / 1.5 * distance * no_flights_ac

                    leaseCost += avgCost_flight[ac_type] * no_flights_ac * distance
                    # dist_acType[ac_type] += distance * no_flights_ac

                # weekly load factor on flight leg
                LF_ij = RPK_ij/ASK_ij

                # weekly operating cost on flight leg
                C_ij    = (Cx_ij + Ct_ij + Cf_ij) * (0.7+0.3*gi*gj) + leaseCost
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


ASK  = pd.DataFrame(ASK_lst,columns=networkData['city'],index=networkData['city'])
RPK  = pd.DataFrame(RPK_lst,columns=networkData['city'],index=networkData['city'])
LF   = pd.DataFrame(LF_lst,columns=networkData['city'],index=networkData['city'])
CASK = pd.DataFrame(CASK_lst,columns=networkData['city'],index=networkData['city'])
RASK = pd.DataFrame(RASK_lst,columns=networkData['city'],index=networkData['city'])
OperProfit = pd.DataFrame(operatingProfit,columns=networkData['city'],index=networkData['city'])

ASK[ASK==0] = np.nan
RPK[RPK==0] = np.nan
LF[LF==0]   = np.nan
CASK[CASK==0] = np.nan
RASK[RASK==0] = np.nan
OperProfit[OperProfit==0] = np.nan

ASK_tot = ASK.sum().sum()
print("Weekly ASK: ", ASK_tot)

RPK_tot = RPK.sum().sum()
print('Weekly RPK: ', RPK_tot)

LF_tot  = RPK_tot/ASK_tot
print('Weekly LF: ', LF_tot)

Cost_tot = (CASK*ASK).sum().sum()
CASK_tot = Cost_tot/ASK_tot
print('Weekly CASK: ', CASK_tot)

Rev_tot  = (RASK*ASK).sum().sum()
RASK_tot = Rev_tot/ASK_tot 
print('Weekly RASK: ', RASK_tot)

# OperProfit_avg  = OperProfit.mean().mean()
# print('Weekly average operating profit: ', OperProfit_avg)

totalProfit     = OperProfit.sum().sum()
print('Weekly total profit: ', totalProfit)

print()
