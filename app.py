from sqlalchemy.sql.operators import isfalse, istrue
import numpy as np
import datetime as dt
from datetime import datetime

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Setup the Database
#################################################
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(engine, reflect=True)

# Save the references to the tables
Measurement = Base.classes.measurement
Stations = Base.classes.station

#################################################
# Flask Setup - format like the class activities
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all routes that are available."""

    return (
        f"----------------------------------------------<br/>"
        f"Welcome to the Climate Application!<br/>"
        f"Available Routes:<br/>"
        f"----------------------------------------------<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"<br/>"
        f"Use the format YYYY-MM-DD when replacing the start_date<br/>"
        f"Use the format YYYY-MM-DD when replacing the start_date and the end_date and separate the dates with a /<br/>"
    )
#--------------------------------------------------------------------
@app.route("/api/v1.0/precipitation")

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary

def precipitation():
    # Create our session(link) from Python to the DB
    session = Session(engine)

    """Return a list of last 12 months of Precipitation data"""

    # Query the most recent date in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Get the date one year from the last date in the dataset
    # That earlier date should be 2016-08-23
    one_year_earlier = (dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d') \
        - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query Precipitation for the last 12 months
    months12_precip = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_earlier).all()

    session.close()

    # Create a dictionary from the row data and append 
    # to a list of precipitation 
    precip_data = []
    for date, prcp in months12_precip:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["precipitation"] = prcp
        precip_data.append(precip_dict)

    return jsonify(precip_data)
#--------------------------------------------------------------------
@app.route("/api/v1.0/stations")

# Return a JSON list of stations from the dataset.

def stations():
    # Create our session(link) from Python to the DB
    session = Session(engine)
    
    """Return a list of last 12 months of Precipitation data"""
    # Query all the Stations
    query_the_stations = session.query(Stations.station, Stations.name).all()
    session.close()
    
    # Create a dictionary from the row data and append to a list of station information
    # This list has station name/location and station id.
    station_info = []
    for station, name in query_the_stations:
        all_stations_dict = {}
        all_stations_dict["station"] = station
        all_stations_dict["name"] = name
        station_info.append(all_stations_dict)

    return jsonify(station_info)
#--------------------------------------------------------------------
@app.route("/api/v1.0/tobs")

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

def tobs():
    # Create our session(link) from Python to the DB
    session = Session(engine)

    """Return a list of dates and temperature observations of the most active station station
    for the last year of data"""

    # Query the most recent data in the dataset
    most_recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    # Query date 12 months prior
    one_year_earlier = (dt.datetime.strptime(most_recent_date[0], '%Y-%m-%d') \
        - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query date and temperature values
    dates_and_temps = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= one_year_earlier).all()

    session.close()

    # Create a dictionary from the row data and append to a list of 
    # dates and temperatures.
    dates_temps_data = []
    for date, tobs in dates_and_temps:
        dates_temps_dict = {}
        dates_temps_dict["date"] = date
        dates_temps_dict["temperature"] = tobs
        dates_temps_data.append(dates_temps_dict)

    return jsonify(dates_temps_data)
#--------------------------------------------------------------------
@app.route("/api/v1.0/<start>")

# Return a JSON list of the minimum temperature, the average temperature, 
# and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for 
# all dates greater than and equal to the start date.

def start_temp_range(start):
    # Create our session(link) from Python to the DB
    session = Session(engine)
    
    # Check to see if the start date is in a valid format YYYY-MM-DD
    # if not then return jsonify message.

    try:
        dt_obj = dt.datetime.strptime(start, "%Y-%m-%d")
        dt_str = dt.datetime.strftime(dt_obj, '%Y-%m-%d')
    except ValueError: 
        return jsonify(f"The wrong start date format {start} was entered")
    
    """Return TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    # Query the min, avg, max of the temperatures for the given start date
    results = session.query(Measurement.date, func.min(Measurement.tobs), \
        func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).group_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of 
    # date and temperature observations
    start_temp_data = []
    for date, minimum, average, maximum in results:

        start_temp_dict = {}
        start_temp_dict["Date"] = date
        start_temp_dict["TMIN"] = minimum
        start_temp_dict["TAVG"] = average
        start_temp_dict["TMAX"] = maximum
        start_temp_data.append(start_temp_dict)

    return jsonify(start_temp_data)
    
    session.close()
#--------------------------------------------------------------------
@app.route("/api/v1.0/<start>/<end>")
def start_end_range(start,end):
    # Create our session(link) from Python to the DB
    session = Session(engine)

    # Check to see if the start date is in a valid format YYYY-MM-DD
    # if not then return jsonify message.

    try:
        dt_obj1 = dt.datetime.strptime(start, "%Y-%m-%d")
        dt_str1 = dt.datetime.strftime(dt_obj1, '%Y-%m-%d')
    except ValueError: 
        return jsonify(f"The wrong start date format {start} was entered")

    # Check to see if the end date is in a valid format YYYY-MM-DD
    # if not then return jsonify message.

    try:
        dt_obj2 = dt.datetime.strptime(end, "%Y-%m-%d")
        dt_str2 = dt.datetime.strftime(dt_obj2, '%Y-%m-%d')
    except ValueError: 
        return jsonify(f"The wrong end date format {end} was entered")    
     
    """Return TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

    # Query the min, avg, max for dates between the start and end date inclusive
    results = session.query(Measurement.date, func.min(Measurement.tobs), \
        func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).\
                filter(Measurement.date <= end).\
                    group_by(Measurement.date).all()

    # Create a dictionary from the row data and append to a list of 
    # date and tobs
    start_end_tobs_data = []
    for date, minimum, average, maximum in results:
        start_end_tobs_dict = {}
        start_end_tobs_dict["Date"] = date
        start_end_tobs_dict["TMIN"] = minimum
        start_end_tobs_dict["TAVG"] = average
        start_end_tobs_dict["TMAX"] = maximum
        start_end_tobs_data.append(start_end_tobs_dict)

    return jsonify(start_end_tobs_data)

    session.close()
#--------------------------------------------------------------------

if __name__ == '__main__':

    app.run(debug=True)
