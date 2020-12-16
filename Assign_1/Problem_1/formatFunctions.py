import demand_globalData as globals
import numpy as np
import pandas as pd
import ast



def formatOutput(m):

    networkData = globals.networkData

    x_optimised = pd.DataFrame(columns=networkData['ICAO'], index=networkData['ICAO'])  # Direct flow from airport i to j
    w_optimised = pd.DataFrame(columns=networkData['ICAO'], index=networkData['ICAO'])  # Direct flow from airport i to j
    z_optimised = pd.DataFrame(columns=networkData['ICAO'], index=networkData['ICAO'])  # Direct flow from airport i to j
    AC_optimised = pd.DataFrame(columns=['Number of AC'])
    for i in range(len(networkData['ICAO'])):
        for j in range(len(networkData['ICAO'])):
            z_optimised.iloc[i, j] = []

    for var in m.getVars():
        if var.x:
            if var.VarName[0] == 'x':
                name_1 = var.VarName.split('[')[-1]
                name_2 = name_1.split(']')[0]
                loc = name_2.split(',')
                i = int(loc[0])
                j = int(loc[1])

                x_optimised.iloc[i,j] = var.x

            elif var.varName[0] == 'w':
                name_1 = var.VarName.split('[')[-1]
                name_2 = name_1.split(']')[0]
                loc = name_2.split(',')
                i = int(loc[0])
                j = int(loc[1])

                w_optimised.iloc[i,j] = var.x

            elif var.varName[0] == 'z':
                name_1 = var.VarName.split('[')[-1]
                name_2 = name_1.split(']')[0]
                loc = name_2.split(',')
                i = int(loc[0])
                j = int(loc[1])
                k = int(loc[2])

                z_optimised.iloc[i,j].append([k, var.x])

            else:
                ACnumber = int(var.VarName[-2])
                input = np.array([ACnumber, var.x])
                AC_optimised.loc['AC type '+str(ACnumber)] = var.X

    x_optimised[x_optimised.isnull()] = '-'
    w_optimised[w_optimised.isnull()] = '-'
    z_optimised[z_optimised.isnull()] = '-'

    with pd.ExcelWriter('optimizationOutput.xlsx') as writer:  
        x_optimised.to_excel(writer, sheet_name='x_ij')  
        w_optimised.to_excel(writer, sheet_name='w_ij')  
        z_optimised.to_excel(writer, sheet_name='z_ij')  
        AC_optimised.to_excel(writer, sheet_name='AC')  

    return


def readOptimizedData():
    x_ij = pd.read_excel(open('optimizationOutput.xlsx', 'rb'),sheet_name='x_ij',index_col=0)
    w_ij = pd.read_excel(open('optimizationOutput.xlsx', 'rb'),sheet_name='w_ij',index_col=0)
    z_ij = pd.read_excel(open('optimizationOutput.xlsx', 'rb'),sheet_name='z_ij',index_col=0)
    AC   = pd.read_excel(open('optimizationOutput.xlsx', 'rb'),sheet_name='AC')

    x_ij[x_ij == '-'] = 0
    w_ij[w_ij == '-'] = 0
    z_ij[z_ij == '[]'] = 0


    return x_ij, w_ij, z_ij, AC


