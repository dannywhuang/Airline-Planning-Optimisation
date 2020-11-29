from math import sqrt, asin, sin, cos, pow, pi
import pandas as pd
import numpy as np
from scipy.stats import norm
from scipy.linalg import lstsq
import matplotlib.pyplot as plt

def calculateDistance(lat1, lat2, long1, long2):
    t1 = pow(sin((lat1-lat2)/2*(pi/180)), 2)
    t2 = cos(lat1*(pi/180)) * cos(lat2*(pi/180)) * pow(sin((long1-long2)/2*(pi/180)), 2)
    deltaSigma = 2 * asin(sqrt(t1+t2))
    distance = 6371 * deltaSigma
    return distance

def check_symmetric(a, rtol=1e-05, atol=1e-08):
    return np.allclose(a, a.T, rtol=rtol, atol=atol)

fuelCost = 1.42

population = pd.read_excel('general_data.xlsx', usecols = 'A:C', skiprows = 2)
gdp = pd.read_excel('general_data.xlsx', usecols = 'E:G', skiprows = 2)
N = gdp.shape[0]    # N is the number of cities
print(N)

#print(calculateDistance(52.379189, 52.520008, 4.899431, 13.404954))                  # verified using online calculator

latLong = pd.read_excel('demand_data.xlsx', index_col = 0, usecols = 'B:V', skiprows = 3, nrows = 3)
demand  = pd.read_excel('demand_data.xlsx', index_col = 0, usecols = 'B:V', skiprows = 11, nrows = 20).values

ICAO = latLong.iloc[0, :].to_list()
latitude = latLong.iloc[1, :].to_numpy()
longitude = latLong.iloc[2, :].to_numpy()
print(ICAO)

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


A = np.ones((len(demandLn), 4))
A[:, 1] = popLn
A[:, 2] = GDPLn
A[:, 3] = distLn

p, res, rnk, s  = lstsq(A, demandLn)
print('res is ', res)
print('k = ', np.exp(p[0]))
print('b1 = ', p[1])
print('b2 = ', p[2])
print('b3 = ', p[3])
kLn = p[0]
k = np.exp(p[0])
b1 = p[1]
b2 = p[2]
b3 = p[3]

# verification - error

plt.figure('Verification - Histogram')

demand_computed = np.array([])
demand_data = np.array([])
for i in range(N):
    for j in range(N):
        if i != j:
            Dij_comp = k * (population2015[i]*population2015[j])**b1 * (gdp2015[i]*gdp2015[j])**b2 / (fuelCost*calculateDistance(latitude[i], latitude[j], longitude[i], longitude[j]))**b3
            Dij_data = demand[i,j]

            demand_computed = np.append(demand_computed, Dij_comp)
            demand_data = np.append(demand_data, Dij_data)

error = demand_computed - demand_data
# error = error[error<200]

mu, std = norm.fit(error)

plt.title('Histogram of the error for the 2015 demand')
plt.hist(error, 100)

xmin, xmax = plt.xlim()

plt.figure('Normal distribution')
x = np.linspace(-150, 150, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'k')
normDistrTitle = '$\mu$ ' + str(round(mu,2)) + ', $\sigma$ ' + str(round(std,2))
plt.title(normDistrTitle)
plt.grid()
plt.xlabel('Error')


# verification - prediction and real
demand_computed = np.exp(kLn+b1*popLn + b2*GDPLn + b3*distLn)
demand_data     = np.exp(demandLn)
print("Length of demand computed ", len(demand_computed))
demand_error    = sum(abs(demand_computed - demand_data))/len(demand_computed)
print("Average error ", demand_error)

# plot prediction and real
plt.figure('Verification ')
x = range(len(demand_computed))
plt.scatter(x, demand_computed, color= 'red')
plt.scatter(x, demand_data, color='blue')
# plt.show()


# 2020 data forecast
gdp2020 = np.array([])
pop2020 = np.array([])

for i in range(N):

    x = np.vstack((len(gdp2015)*[2015], len(gdp2015)*[2018]))

    y = np.vstack((gdp2015,  gdp2018))
    coeff = np.polyfit(x[:, i], y[:,i], 1)
    eq = np.poly1d(coeff)
    gdp2020 = np.append(gdp2020, eq(2020))

    y2 = np.vstack((population2015, pop2018))
    coeff = np.polyfit(x[:, i], y2[:, i], 1)
    eq = np.poly1d(coeff)
    pop2020 = np.append(pop2020, eq(2020))

plt.figure('Verification GDP forecast')
x = range(N)
plt.plot(x,gdp2015,'b*',label='2015')
plt.plot(x,gdp2018,'k*',label='2018')
plt.plot(x,gdp2020,'r*',label='2020')
plt.legend()
# plt.show()

plt.figure('Verification POP forecast')
x = range(N)
plt.plot(x,population2015,'b*',label='2015')
plt.plot(x,pop2018,'k*',label='2018')
plt.plot(x,pop2020,'r*',label='2020')
plt.legend()

demand2020_forecast = np.zeros((N, N))

for i in range(N):
    for j in range(N):
        if i!=j:
            demand2020_forecast[i, j] = k*pow(pop2020[i]*pop2020[j], b1)*pow(gdp2020[i]*gdp2020[j], b2)/pow(fuelCost*calculateDistance(latitude[i], latitude[j], longitude[i], longitude[j]), b3)

demand2015_comp = np.zeros((N, N))
for i in range(N):
    for j in range(N):
        if i!=j:
            demand2015_comp[i, j] = k*pow(population2015[i]*population2015[j], b1)*pow(gdp2015[i]*gdp2015[j], b2)/pow(fuelCost*calculateDistance(latitude[i], latitude[j], longitude[i], longitude[j]), b3)

demand2015_lst = np.reshape(demand, (1,N*N))[0]
demand2015computed_lst = np.reshape(demand2015_comp, (1,N*N))[0]
demand2018_lst = np.reshape(demand, (1,N*N))[0]
demand2020_lst = np.reshape(demand2020_forecast, (1,N*N))[0]
demand2020_comparison = np.reshape(demand2020_forecast - demand,(1,N*N))[0]
demand2020_comparison = demand2020_lst - demand2015_lst

plt.figure('Verification demand forecast')
plt.title('Change in demand in 2020 compared to 2015')
x = range(N*N)
plt.stem(x,demand2020_comparison,'b*')
# plt.plot(x,demand2020_lst,'r*',label='2020')
plt.legend()
plt.show()

demand2020_forecast_df = pd.DataFrame(np.round(demand2020_forecast, 1), index = ICAO, columns = ICAO)
demand2020_forecast_df.to_excel('demand2020_forecast.xlsx')


plt.show()