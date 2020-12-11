"""
Name: Zachary Chin
CS230: Section SN4
Data: Boston Uber and Lyft Rideshare Data Sample
URL:

Description: This program takes data from the sample of Uber and Lyft rides and analyzes it in various ways. It will create
             GridLayer map that tells how many rides are taken from somewhere. It will also create two bar graphs based
             on either qualitative or quantitative data. This will all be put into a website using streamlit and can
             be interacted with by users.
"""
import pandas as pd
import streamlit as st
import pydeck as pdk
import numpy as np
import matplotlib.pyplot as plt
from datetime import time

MAPKEY = "pk.eyJ1IjoiemNoaW4iLCJhIjoiY2tpaTZ1bnV5MDBtazJ0cjM2aWYxeWx0ciJ9.gJsBdyaQ0ZFm53amr-acnA"
FILENAME = "ridesharesample.csv"
COLUMNS = ["day", "month", "datetime", "source", "destination", "cab_type", "price", "distance",
           "latitude", "longitude", "temperature", "apparentTemperature", "short_summary", "long_summary"]
sourceDict = {"Beacon Hill": [42.3588, -71.0707], "Theatre District": [42.3519, -71.0643], "Financial District": [42.3559, -71.0550],
              "Back Bay": [42.3503, -71.0810], "Northeastern University": [42.3398, -71.0892], "Boston University": [42.3505, -71.1054],
              "Fenway": [42.3467, -71.0972], "West End": [42.3644, -71.0661], "Haymarket Square": [42.3638, -71.0585], "North End": [42.3647, -71.0542],
              "South Station": [42.3519, -71.0552], "North Station": [42.3663, -71.0622]}

# importing the dataframe from ridesharesample.csv
rideshare = pd.read_csv(FILENAME, usecols=COLUMNS)

st.title("CS230 Final Project")


def addLatitude(row):
    # Adds a latitude column to the dataset based on the source of the ride
    lat = sourceDict[row["source"]][0]
    return lat


def addLongitude(row):
    # Adds a longitude column to the dataset based on the source of the ride
    lon = sourceDict[row["source"]][1]
    return lon


def bin(max, min):
    # creates what range the columns of the bar chart will take data from
    dataRange = max - min
    binSize = dataRange // 5
    return binSize


def createMap():
    # Creates the map that can be changed by the user
    st.subheader("The impact time of day has on where the ride is being taken from")
    # creates the slider
    timeRange = st.slider("Choose a range of times", value=(time(00, 00), time(23, 59)))

    # creates the side by side data with the map and the check boxes
    col1, col2 = st.beta_columns([3, 1])
    col1.subheader("Map of where people are taking rides from")
    col2.write("Choose which locations to show")

    # creates the list of source locations that will be included in the map
    chosenList = []
    for area in sourceDict.keys():
        area_Status = col2.checkbox(area, value=True)
        if area_Status:
            chosenList.append(area)

    # creates the data frame times with only the latitude, longitude, source locations, and time of ride (which is in the user specified range
    rideshare["time"] = rideshare["datetime"].str[11:]
    rideshare["time"] = pd.to_datetime(rideshare["time"])
    rideshare["datetime"] = pd.to_datetime(rideshare["datetime"])
    times = rideshare[rideshare['time'].between(timeRange[0].strftime('%H:%M'), timeRange[1].strftime('%H:%M'))]  # removes data not in the right time range
    times = times.drop(columns=["day", "month", "datetime", "cab_type", "price", "distance", "temperature", "apparentTemperature", "short_summary", "long_summary"])

    # Creates the final dataframe that will be used in the map with only data in from the specified source location
    mapData = times[times["source"].isin(chosenList)]

    # uses the functions addLatitude and addLongitude to create the columns with the right lat ann lon values
    mapData["lat"] = mapData.apply(addLatitude, axis=1)
    mapData["lon"] = mapData.apply(addLongitude, axis=1)

    # Creates the map as a GridLayer map
    tool_tip = {"html": "Location: <b>{source}</b> <b>Count: {count}</b>",
                "style":
                    {"color": "white"}}
    layer = pdk.Layer("GridLayer", mapData, pickable=True, extruded=True, cell_size=300, elevation_scale=5, get_position=["lon", "lat"])
    view_state = pdk.ViewState(latitude=mapData["lat"].mean(), longitude=mapData["lon"].mean(), zoom=11, pitch=45, bearing=30)
    timeMap = pdk.Deck(layers=[layer], initial_view_state=view_state, mapbox_key=MAPKEY, tooltip=tool_tip)

    col1.pydeck_chart(timeMap)


def chooseNumeric():
    # Has the user choose data to be used in a bar graph
    st.subheader("How does different quantitative properties impact the usage of either Uber or Lyft")

    # creates the dataframe that holds the chosen data and lets the user choose what is in it
    chosenData = pd.DataFrame()
    options = ["temperature", "apparentTemperature", "price", "distance"]
    choice = st.radio("Choose data to make a graph of", options=options)
    chosenData["cab_type"] = rideshare["cab_type"]
    chosenData["numbers"] = rideshare[choice]
    # this is for making the pivot table later, so we can sum the amount of rides for each category
    chosenData["rides"] = 1

    # Creates the bins that the data is sorted into, so that it can be made into a bar graph
    binSize = bin(chosenData["numbers"].max(), chosenData["numbers"].min())
    binDict = {}
    for n in range(5):
        binDict[f"{chosenData['numbers'].min() + binSize * n:.2f}" + " to " + f"{chosenData['numbers'].min() + binSize * (1 + n):.2f}"] \
            = [chosenData["numbers"].min() + binSize * n, chosenData["numbers"].min() + binSize * (1 + n)]

    def addBins(row):
        for key in binDict.keys():
            if (row["numbers"] >= binDict[key][0]) and (row["numbers"] < binDict[key][1]):
                return key

    chosenData["option"] = chosenData.apply(func=addBins, axis=1)

    # puts the chosen data into the bar graph creating function
    createBar(chosenData)


def chooseQualitative():
    # makes the user choose a qualitative property to make a bar graph of
    st.subheader("How do different qualitative properties impact the usage of either Uber or Lyft")
    # creates a dataframe of the data that the user chooses
    chosenData = pd.DataFrame()
    options = ["short_summary", "long_summary"]
    choice = st.radio("Choose a type of weather summary to make a bar graph of:", options=options)
    chosenData["cab_type"] = rideshare["cab_type"]
    chosenData["option"] = rideshare[choice]
    # this is for making the pivot table later, so we can sum the amount of rides for each category
    chosenData["rides"] = 1
    # puts the chosen data into the bar graph creating function
    createBar(chosenData)


def createBar(df):
    # Creates a bar graph based on a dataframe passed into the function
    # creates a pivot table based on the data the user chose and
    table = pd.pivot_table(data=df, index=["option"], columns=["cab_type"], values=["rides"], aggfunc=np.sum, fill_value=0)
    # plots the pivot table with a legend, and the amount of rides (in a christmas theme)
    table.plot(kind="bar", color=["red", "green"], edgecolor="white")
    plt.legend(labels=["Lyft", "Uber"])
    plt.xlabel("")
    plt.ylabel("Rides")
    plt.xticks(rotation=30, ha="right")
    ax = plt.gca()
    ax.set_facecolor("black")
    st.pyplot(plt)

def main():
    createMap()
    chooseNumeric()
    chooseQualitative()


main()
