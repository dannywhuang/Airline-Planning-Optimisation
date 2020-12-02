import demand_loadData as load
import demand_functions as funct
import demand_globalData as globals
import matplotlib.pyplot as plt

# Load input data from excel and structurize it into panda dataframes
airlineData = load.loadData()

# Calibrate the gracity function based on the given 2015 demand
[globals.k, globals.b1, globals.b2, globals.b3] = funct.gravityModelCalibration(airlineData['2015'])
funct.VVgravityModel(airlineData['2015'])   # plot error between the gravity function and data

# Compute the forecasted 2018 demand and append that to the 2018 data frame
demand2018_forecast = funct.gravityModel(airlineData['2018'])
airlineData['2018']['demand'] = demand2018_forecast
funct.VVdemandForecast(airlineData['2018'], airlineData['2015'])    # plot the difference in demand

# Compute the forecasted 2020 population anc GDP and append that to the 2020 data frame
population2020_forecast, GDP2020_forecast = funct.linearCityDataInterp('2020', airlineData['2015'], airlineData['2018'])
airlineData['2020']['pop'] = population2020_forecast
airlineData['2020']['GDP'] = GDP2020_forecast

# Compute the forecasted 2020 demand and append that to the 2020 data frame
demand2020_forecast = funct.gravityModel(airlineData['2020'])
airlineData['2020']['demand'] = demand2020_forecast
funct.VVdemandForecast(airlineData['2020'], airlineData['2015'])    # plot the difference in demand
funct.VVdemandForecast(airlineData['2020'], airlineData['2018'])    # plot the difference in demand

print()
plt.show()