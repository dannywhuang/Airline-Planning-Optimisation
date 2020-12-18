from formatFunctions import readOptimizedData
import demand
import demand_globalData as globals
import demand_functions as funct
import aircraft_loadData as aircraftLoad
import ast

demand.demandForecast()
networkData = globals.networkData
aircraftData = aircraftLoad.loadData()
aircraft = range(len(aircraftData.columns))

x_ij, w_ij, z_ij, AC = readOptimizedData()

airports_lst = networkData['city'].to_numpy()
No_airports  = len(airports_lst)

rev = 0
for i in range(No_airports):
    for j in range(No_airports):
        if i!=j:
            origin = airports_lst[i]  # To check the current airport origin
            dest = airports_lst[j]  # To check the current airport destination
            distance = funct.calculateDistance(origin, dest)
            gi = 1
            gj = 1
            if origin == 'Paris':
                gi = 0
            if dest == 'Paris':
                gj = 0

            transfer_ij = w_ij.iloc[i, j]
            direct_ij = x_ij.iloc[i, j]
            yield_ij = 5.9 * distance ** (-0.76) + 0.043
            rev += yield_ij*distance*(transfer_ij+direct_ij)

print("revenue is", rev)

opCost = 0
for i in range(No_airports):
    for j in range(No_airports):
        if i!=j:
            origin = airports_lst[i]  # To check the current airport origin
            dest = airports_lst[j]  # To check the current airport destination
            distance = funct.calculateDistance(origin, dest)
            gi = 1
            gj = 1
            if origin == 'Paris':
                gi = 0
            if dest == 'Paris':
                gj = 0

            if z_ij.iloc[i, j] != 0:
                zij = ast.literal_eval(z_ij.iloc[i, j])

                for k in range(len(zij)):
                    ac_type = zij[k][0]
                    no_flights_ac = zij[k][1]
                    singleAircraftData = aircraftData.iloc[:, ac_type]

                    cTk = singleAircraftData['Time cost parameter']  # time based costs
                    cfk = singleAircraftData['Fuel cost parameter']  # fuel cost
                    spk = singleAircraftData['Speed']  # speed of aircraft
                    # CLk = singleAircraftData['Weekly lease cost']
                    CXk = singleAircraftData['Fixed operating cost']


                    opCost += (0.7 + 0.3*gi*gj) * (CXk + cTk * distance/spk + cfk*1.42/1.5*distance)*zij[k][1]

print("operational costs", opCost)

# Total ac lease cost
Cl = 0
for ac in AC.iloc[:,0]:
    ac_type = int(ac[-1])
    leaseCost = aircraftData.loc['Weekly lease cost','Aircraft '+str(int(ac_type+1))] 
    no_flights_ac = float(AC.loc[ac_type,'Number of AC'])
    Cl += leaseCost * no_flights_ac

print("lease cost", Cl)
print("net revenue", (rev-opCost-Cl))

