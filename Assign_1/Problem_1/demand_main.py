import demand_loadData as load
import demand_functions as funct
import demand_globalData as globals

airlineData = load.loadData()

[globals.k, globals.b1, globals.b2, globals.b3] = funct.gravityModelCalibration(airlineData['2015'])



test = funct.gravityModel(airlineData['2018'])

print()