from datetime import *
from lib2to3.pgen2.token import NEWLINE
from os import stat
import geopy as gp
import pandas as pd
from geopy.distance import geodesic as GD

# Grabbing csv files data and putting into database obj
satelliteData = pd.read_csv(
    r"C:\Users\micha\Desktop\Python Files\Satellite.csv", encoding='cp1252', on_bad_lines='skip')
csData = pd.read_csv(
    r"C:\Users\micha\Desktop\Python Files\CitizenScience.csv", encoding='cp1252', on_bad_lines='skip')

# Converting dates in csv to Datetime obj for later use
satelliteData['Date'] = pd.to_datetime(
    satelliteData['Date'], format='%b/%d/%Y')
csData['Date'] = pd.to_datetime(csData['Date'], format='%m/%d/%Y')

# Sorting by date
csData.sort_values(by='Date', inplace=True)
satelliteData.sort_values(by='Date', inplace=True)

# Get specific parameters for search
print('Enter radius to search for inconsistent points (m) :')
searchDistance = int(input())
print('Enter range of time to search in (days) :')
timeRange = int(input())
print('Enter minimum density difference to look for :')
densityRange = float(input())

# Compares all locations' Sargassum density based on searchDistance, timeRange, and densityRange
for x in satelliteData.index:
    date = satelliteData.loc[x, 'Date']
    for y in csData.index:
        csDate = csData.loc[y, 'Date']
        dateDiff = date - csDate
        if (abs(dateDiff) <= timedelta(days=timeRange)):
            densityDiff = abs(
                satelliteData.loc[x, 'DENSITY'] - csData.loc[y, 'DENSITY'])
            distance = GD((satelliteData.loc[x, 'Latitude'], satelliteData.loc[x, 'Longitude']), (
                csData.loc[y, 'Lat'], csData.loc[y, 'Lon'])).m

            if (densityDiff > densityRange and distance <= searchDistance):
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


print("Finished")
