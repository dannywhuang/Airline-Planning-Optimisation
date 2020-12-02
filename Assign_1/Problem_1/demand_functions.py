from math import sqrt, asin, sin, cos, pow, pi
import numpy as np
from scipy.linalg import lstsq
from scipy.stats import norm
import demand_globalData as globals
import matplotlib.pyplot as plt


def calculateDistance(origin,destination):

    networkData = globals.networkData
    ICAO_lst = networkData['ICAO']
    city_lst = networkData['city']
    lat_lst  = networkData['lat']
    long_lst = networkData['long']
    
    if origin in ICAO_lst:
        indexOrig = origin==ICAO_lst
        indexDest = destination==ICAO_lst
    elif origin in city_lst:
        indexOrig = origin==city_lst
        indexDest = destination==city_lst
    
    t1 = pow(sin((lat_lst[indexOrig][0] - lat_lst[indexDest][0])/2*(pi/180)), 2)
    t2 = cos(lat_lst[indexOrig][0]*(pi/180)) * cos(lat_lst[indexDest][0]*(pi/180)) * pow(sin((long_lst[indexOrig][0]-long_lst[indexDest][0])/2*(pi/180)), 2)
    deltaSigma = 2 * asin(sqrt(t1+t2))
    distance = 6371 * deltaSigma
    return distance


def gravityModelCalibration(calibrationData):

    fuelCost = globals.fuelCost

    population_lst  = calibrationData['pop']
    GDP_lst         = calibrationData['GDP']
    demand_lst      = calibrationData['demand']

    networkData     = globals.networkData
    city_lst        = networkData['city']

    ICAO_lst = networkData['ICAO']

    demand_lin = np.array([])
    pop_lin    = np.array([])
    GDP_lin    = np.array([])
    dist_lin   = np.array([])

    for origin in ICAO_lst:
        for dest in ICAO_lst:
            if origin!=dest:
                indexOrig  = origin==ICAO_lst
                indexDest  = dest==ICAO_lst

                cityOrig = city_lst[indexOrig][0]
                cityDest = city_lst[indexDest][0]

                demand  = demand_lst[indexOrig,indexDest][0]
                popOrig = population_lst[indexOrig][0]
                popDest = population_lst[indexDest][0]
                GDPOrig = GDP_lst[indexOrig]
                GDPDest = GDP_lst[indexDest]
                distance= calculateDistance(origin,dest)

                demand_lin  = np.append(demand_lin, np.log(demand))
                pop_lin     = np.append(pop_lin, np.log(popOrig * popDest))
                GDP_lin     = np.append(GDP_lin, np.log(GDPOrig * GDPDest))
                dist_lin    = np.append(dist_lin, - np.log(fuelCost * distance))

    A = np.ones((len(demand_lin), 4))
    A[:, 1] = pop_lin
    A[:, 2] = GDP_lin
    A[:, 3] = dist_lin

    p, res, rnk, s  = lstsq(A, demand_lin)
    # print('res is ', res)
    # print('k = ', np.exp(p[0]))
    # print('b1 = ', p[1])
    # print('b2 = ', p[2])
    # print('b3 = ', p[3])
    kLn = p[0]
    k = np.exp(p[0])
    b1 = p[1]
    b2 = p[2]
    b3 = p[3]

    return [k, b1, b2, b3]


def gravityModel(dataSet):

    k  = globals.k
    b1 = globals.b1
    b2 = globals.b2
    b3 = globals.b3

    networkData = globals.networkData
    fuelCost    = globals.fuelCost

    population_lst = dataSet['pop']
    GDP_lst        = dataSet['GDP']
    city_lst       = dataSet['city']

    ICAO_lst = networkData['ICAO']
    numberOfAirports = len(ICAO_lst)

    demand_lst = np.array([])

    for origin in ICAO_lst:
        for dest in ICAO_lst:
            if origin!=dest:
                indexOrig  = origin==ICAO_lst
                indexDest  = dest==ICAO_lst

                cityOrig = city_lst[indexOrig][0]
                cityDest = city_lst[indexDest][0]

                popOrig = population_lst[indexOrig][0]
                popDest = population_lst[indexDest][0]
                GDPOrig = GDP_lst[indexOrig][0]
                GDPDest = GDP_lst[indexDest][0]
                distance= calculateDistance(origin,dest)

                demand = k * (popOrig*popDest)**b1 * (GDPOrig*GDPDest)**b2 / (fuelCost*distance)**b3
                demand_lst = np.append(demand_lst, demand)
            
            if origin==dest:
                demand = 0
                demand_lst = np.append(demand_lst, demand)

    demand_lst = demand_lst.astype(int)
    # demand_lst = np.round(demand_lst,1)
    demand_lst = np.reshape(demand_lst, (numberOfAirports,numberOfAirports))

    return demand_lst


def linearCityDataInterp(targetYear, dataSet1, dataSet2):

    targetYear = int(targetYear)
    year1 = int(dataSet1['year'])
    year2 = int(dataSet2['year'])

    cities_lst = dataSet1['city']
    numberOfCities = len(cities_lst)

    popYear1_lst = dataSet1['pop']
    popYear2_lst = dataSet2['pop']
    GDPyear1_lst = dataSet1['GDP']
    GDPyear2_lst = dataSet2['GDP']

    # 2020 data forecast
    GDPtarget_lst = np.array([])
    popTarget_lst = np.array([])

    for city in range(numberOfCities):

        x = np.vstack((len(GDPyear1_lst)*[year1], len(GDPyear1_lst)*[year2]))

        y = np.vstack((GDPyear1_lst,  GDPyear2_lst))
        coeff = np.polyfit(x[:, city], y[:, city], 1)
        eq = np.poly1d(coeff)
        GDPtarget_lst = np.append(GDPtarget_lst, eq(targetYear))

        y2 = np.vstack((popYear1_lst, popYear2_lst))
        coeff = np.polyfit(x[:, city], y2[:, city], 1)
        eq = np.poly1d(coeff)
        popTarget_lst = np.append(popTarget_lst, eq(targetYear))

    return popTarget_lst, GDPtarget_lst


def VVgravityModel(comparisonData):

    year           = comparisonData['year']
    demandData     = comparisonData['demand']
    demandComputed = gravityModel(comparisonData)

    numberOfAirports = len(comparisonData['city'])
    demandData_lst = np.reshape(demandData,(1,numberOfAirports*numberOfAirports))[0]
    demandComputed_lst = np.reshape(demandComputed,(1,numberOfAirports*numberOfAirports))[0]

    error = demandComputed_lst - demandData_lst
    # error = error[0]
    # error = error[error<200]

    mu, std = norm.fit(error)

    plt.figure('Gravity Model Error')
    plt.subplot(2,1,1)
    plt.title('Histogram of the error of the '+str(year)+' demand')
    plt.hist(error, 100, edgecolor='k')

    xmin, xmax = plt.xlim()

    plt.subplot(2,1,2)
    x = np.linspace(-150, 150, 100)
    p = norm.pdf(x, mu, std)
    plt.plot(x, p, 'k')
    normDistrTitle = '$\mu$ ' + str(round(mu,2)) + ', $\sigma$ ' + str(round(std,2))
    plt.title(normDistrTitle)
    plt.grid()
    plt.xlabel('Error - Demand')

    return


def VVdemandForecast(forecastData, initialData):

    yearInit        = initialData['year']
    yearForecast    = forecastData['year']
    demandInit      = initialData['demand']
    demandForecast  = forecastData['demand']

    numberOfAirports = len(initialData['city'])
    demandData_lst = np.reshape(demandInit,(1,numberOfAirports * numberOfAirports))[0]
    demandForecast_lst = np.reshape(demandForecast,(1,numberOfAirports * numberOfAirports))[0]

    demandDifference = demandForecast_lst - demandData_lst

    plt.figure('Verification '+str(yearForecast)+' demand forecast compared to '+str(yearInit))
    plt.title('Change in demand in '+str(yearForecast)+' compared to '+str(yearInit))
    x = range(numberOfAirports * numberOfAirports)
    plt.stem(x,demandDifference,'b*')

    return

