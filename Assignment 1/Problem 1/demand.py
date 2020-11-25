from math import sqrt, asin, sin, cos, pow, pi
import pandas as pd
import numpy as np
from scipy.linalg import lstsq

def calculateDistance(lat1, lat2, long1, long2):
    t1 = pow(sin((lat1-lat2)/2*(pi/180)), 2)
    t2 = cos(lat1*(pi/180)) * cos(lat2*(pi/180)) * pow(sin((long1-long2)/2*(pi/180)), 2)
    deltaSigma = 2 * asin(sqrt(t1+t2))
    distance = 6371 * deltaSigma
    return distance


fuelCost = 1.42

population = pd.read_excel('general_data.xlsx', usecols = 'A:C', skiprows = 2)
gdp = pd.read_excel('general_data.xlsx', usecols = 'E:G', skiprows = 2)
N = gdp.shape[0]
print(N)

print(calculateDistance(52.379189, 52.520008, 4.899431, 13.404954))                  # verified using online calculator
latLong = pd.read_excel('demand_data.xlsx', index_col = 0, usecols = 'B:V', skiprows = 3, nrows = 3)
demand  = pd.read_excel('demand_data.xlsx', index_col = 0, usecols = 'B:V', skiprows = 11, nrows = 20).values

latitude = latLong.iloc[1, :].to_numpy()
longitude = latLong.iloc[2, :].to_numpy()

demandLn = np.array([])
popLn = np.array([])
GDPLn = np.array([])
distLn = np.array([])

population2015 = population.iloc[:, 1].to_numpy()
pop2018        = population.iloc[:, 2].to_numpy()
gdp2015 = gdp.iloc[:, 1].to_numpy()
gdp2018 = gdp.iloc[:, 2].to_numpy()

for i in range(N):
    for j in range(N):
        if i!=j:
            demandLn = np.append(demandLn, np.log(demand[i,j]))
            popLn = np.append(popLn, np.log(population2015[i] * population2015[j]))
            GDPLn = np.append(GDPLn, np.log(gdp2015[i] * gdp2015[j]))
            distLn = np.append(distLn, - np.log(fuelCost * calculateDistance(latitude[i], latitude[j], longitude[i], longitude[j])))

print(len(demandLn))

A = np.ones((len(demandLn), 4))
A[:, 1] = popLn
A[:, 2] = GDPLn
A[:, 3] = distLn
# print(A)
p, res, rnk, s  = lstsq(A, demandLn)
print(p) # p[0] is ln(k), p[1] is b1, p[2] is b2, p[3] is b3
print('k = ', np.exp(p[0]))
print('b1 = ', p[1])
print('b2 = ', p[2])
print('b3 = ', p[3])


# verification
demand_computed = np.exp(p[0]+p[1]*popLn + p[2]*GDPLn + p[3]*distLn)
demand_data     = np.exp(demandLn)

demand_error    = sum(abs(demand_computed - demand_data))


# 2020 data forecast
gdp2020 = np.array([])
pop2020 = np.array([])

for i in range(N):

      x = np.vstack((len(gdp2015)*[2015], len(gdp2015)*[2018]))

      y = np.vstack((gdp2015,  gdp2018))
      coeff = np.polyfit(x[:,i], y[:,i], 1)
      eq = np.poly1d(coeff)
      gdp2020 = np.append(gdp2020, eq(2020))

      y2 = np.vstack((population2015, pop2018))
      coeff = np.polyfit(x[:, i], y2[:, i], 1)
      eq = np.poly1d(coeff)
      pop2020 = np.append(pop2020, eq(2020))




