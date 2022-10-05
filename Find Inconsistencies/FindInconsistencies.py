from datetime import *
from lib2to3.pgen2.token import NEWLINE
from os import stat
from re import search
import geopy as gp
import pandas as pd
import matplotlib.pyplot as plt
from geopy.distance import geodesic as GD


def look_for_differences(satelliteData, csData):
    # Get specific parameters for search
    print('Enter radius to search for inconsistent points (m) :')
    searchDistance = int(input())
    print('Enter range of time to search in (hours) :')
    timeRange = int(input())
    print('Enter minimum density difference to look for :')
    densityRange = float(input())

    print('Max search radius : ', searchDistance, '\nMax time range : ',
          timeRange, " hours\nMin density difference : ", densityRange)

    # Compares all locations' Sargassum density based on searchDistance, timeRange, and densityRange
    for x in satelliteData.index:
        date = satelliteData.loc[x, 'Date']
        for y in csData.index:
            csDate = csData.loc[y, 'Date']
            dateDiff = date - csDate
            if (abs(dateDiff) <= timedelta(hours=timeRange)):
                densityDiff = abs(
                    satelliteData.loc[x, 'DENSITY'] - csData.loc[y, 'DENSITY'])
                distance = GD((satelliteData.loc[x, 'Latitude'], satelliteData.loc[x, 'Longitude']), (
                    csData.loc[y, 'Lat'], csData.loc[y, 'Lon'])).m

                if (densityDiff >= densityRange and distance <= searchDistance):
                    print(satelliteData.loc[x, 'Site'])
                    print(satelliteData.loc[x, 'Date'])
                    print("Date difference: ", dateDiff)
                    print("CS location: ",
                          csData.loc[y, 'Lat'], ",", csData.loc[y, 'Lon'])
                    print("Satellite location: ", satelliteData.loc[x, 'Latitude'],
                          ",", satelliteData.loc[x, 'Longitude'])

                    print("Density difference: ", densityDiff)
                    print("Distance between points (m): ", distance)
                    print()
            else:
                continue

    print("Finished looking")


def plot(satelliteData, csData):

    # Get parameters for search
    print("What start time? (MM/DD/YYYY) : ")
    startTime = pd.to_datetime(str(input()))
    print("What end time? (MM/DD/YYYY) : ")
    endTime = pd.to_datetime(str(input()))
    print("What coordinates? (LAT,LONG) : ")
    stringList = str(input()).split(",")
    latitude = float(stringList[0])
    longitude = float(stringList[1])
    print("What radius around coordinates? (m)")
    radius = float(input())

    # Makes a subset that only has points within the data range
    csData_subset = csData[(csData['Date'] >=
                           startTime) & (csData['Date'] <= endTime)]
    satelliteData_subset = satelliteData[(satelliteData['Date']
                                         > startTime) & (satelliteData['Date'] < endTime)]

    # Renames the lat/long in satelliteData for my conveinience
    satelliteData_subset.rename(
        columns={'Latitude': 'Lat', 'Longitude': 'Lon'}, inplace=True)
    csData_subset = csData_subset[['Date', 'Lat', 'Lon', 'DENSITY']]
    satelliteData_subset = satelliteData_subset[[
        'Date', 'Lat', 'Lon', 'DENSITY']]

    # Looks at each entry in the subset and sees if it is within radius of the inputted point, if it is, it is added to a list to be plotted (x = date, y = density)
    xPointsSatellite = []
    yPointsSatellite = []
    for x in satelliteData_subset.index:
        if (GD((satelliteData_subset.loc[x, 'Lat'], satelliteData_subset.loc[x, 'Lon']), (latitude, longitude)).m <= radius and not pd.isna(satelliteData_subset.loc[x, 'DENSITY'])):
            xPointsSatellite.append(satelliteData_subset.loc[x, 'Date'])
            yPointsSatellite.append(satelliteData_subset.loc[x, 'DENSITY'])

    xPointsCS = []
    yPointsCS = []
    for y in csData_subset.index:
        if (GD((csData_subset.loc[y, 'Lat'], csData_subset.loc[y, 'Lon']), (latitude, longitude)).m <= radius and not pd.isna(csData_subset.loc[y, 'DENSITY'])):
            yPointsCS.append(csData_subset.loc[y, 'DENSITY'])
            xPointsCS.append(csData_subset.loc[y, 'Date'])

    # Plots data on a graph
    plt.plot(xPointsSatellite, yPointsSatellite, label='Satellite Density')
    plt.plot(xPointsCS, yPointsCS, label='CS Density')
    plt.legend()
    plt.show()


# Grabbing csv files data and putting into database obj
satelliteData = pd.read_csv(
    r"C:\Users\micha\Desktop\Find Inconsistencies\Satellite.csv", encoding='cp1252', on_bad_lines='skip')
csData = pd.read_csv(
    r"C:\Users\micha\Desktop\Find Inconsistencies\CitizenScience.csv", encoding='cp1252', on_bad_lines='skip')

# Removing null and NaN values
satelliteData = satelliteData.dropna()
csData = csData.dropna()

# Converting dates in csv to Datetime obj for later use
satelliteData['Date'] = pd.to_datetime(
    satelliteData['Date'], format='%b/%d/%Y')
csData['Date'] = pd.to_datetime(
    csData['Date'] + " " + csData['Time'], format='%m/%d/%Y %H:%M:%S')


# Sorting by date
csData.sort_values(by='Date', inplace=True)
satelliteData.sort_values(by='Date', inplace=True)

# Gives an option menu
userInput = ''
while (userInput != 'x'):
    print("Press 'l' to look for differences")
    print("Press 'p' to plot a time series")
    print("Press 'x' to exit")
    userInput = str(input())

    if (userInput == 'l'):
        look_for_differences(satelliteData, csData)
    elif (userInput == 'p'):
        plot(satelliteData, csData)
