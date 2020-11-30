import pandas as pd
import numpy as np
import demand_globalData as globals

def loadData():
    # ====================
    # Load data from excel
    # ====================

    excelFileName_1 = 'general_data'
    excelFileName_2 = 'demand_data'

    # Load population data per city
    populationData_excel = pd.read_excel(excelFileName_1 + '.xlsx', usecols = 'A:C', skiprows = 2)
    #   ------
    cities  = populationData_excel.iloc[:, 0].to_numpy()
    pop2015 = populationData_excel.iloc[:, 1].to_numpy()
    pop2018 = populationData_excel.iloc[:, 2].to_numpy()

    # Load GDP data per country (USD)
    GDPData_excel = pd.read_excel(excelFileName_1 + '.xlsx', usecols = 'E:G', skiprows = 2)
    #   ------
    countries = GDPData_excel.iloc[:, 0].to_numpy()
    gdp2015   = GDPData_excel.iloc[:, 1].to_numpy()
    gdp2018   = GDPData_excel.iloc[:, 2].to_numpy()

    # Load airport data for airline
    airportData_excel = pd.read_excel(excelFileName_2 + '.xlsx', index_col = 0, usecols = 'B:V', skiprows = 3, nrows = 5)
    #   ------
    ICAO        = airportData_excel.iloc[0, :].to_numpy()
    latitude    = airportData_excel.iloc[1, :].to_numpy()
    longitude   = airportData_excel.iloc[2, :].to_numpy()
    runway      = airportData_excel.iloc[3, :].to_numpy()
    slots       = airportData_excel.iloc[4, :].to_numpy()

    # Load demand per week
    demandData_excel  = pd.read_excel(excelFileName_2 + '.xlsx', index_col = 0, usecols = 'B:V', skiprows = 11, nrows = 20)
    #   ------
    demand2015 = demandData_excel.values

    # ==============================
    # Add data to created dataframes
    # ==============================

    data2015 = {}
    data2018 = {}
    networkData = {}

    data2015['city']    = cities
    data2015['country'] = countries
    data2015['pop']     = pop2015
    data2015['GDP']     = gdp2015
    data2015['demand']  = demand2015

    data2018['city']    = cities
    data2018['country'] = countries
    data2018['pop']     = pop2018
    data2018['GDP']     = gdp2018

    networkData['city']    = cities
    networkData['country'] = countries
    networkData['ICAO']    = ICAO 
    networkData['lat']     = latitude
    networkData['long']    = longitude
    networkData['rnw']     = runway
    networkData['slots']   = slots

    airlineData = {}

    airlineData['2015'] = data2015
    airlineData['2018'] = data2018

    globals.networkData = networkData

    return airlineData

