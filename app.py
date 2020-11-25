#
# Hawaiian Climate
#
# A series of API calls to get various Hawaiian climate data
#

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to the tables
Measurements = Base.classes.measurement
Stations = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Base route, API specs


@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;"
    )

#
# Get the precipitation list for entire Hawaii
#


@app.route("/api/v1.0/precipitation")
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the DB
    results = session.query(
        Measurements.date, Measurements.prcp).order_by(Measurements.date)

    # Loop through and build dictionary list
    precipitation_list = []
    for date, precipitation in results:
        precip = {}
        precip[date] = precipitation
        precipitation_list.append(precip)

    # Close the session we don't want to run out of resources
    session.close()

    return jsonify(precipitation_list)


@app.route("/api/v1.0/stations")
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the DB
    results = session.query(Stations.station, Stations.name)

    # Loop through and build dictionary list
    station_list = []
    for station, name in results:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_list.append(station_dict)

    # Close the session we don't want to run out of resources
    session.close()

    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the DB for most active station
    results = session.query(Measurements.station, Stations.name, func.count(Measurements.tobs)).\
        filter(Measurements.station == Stations.station).\
        group_by(Measurements.station).\
        order_by(func.count(Measurements.tobs).desc())

    # Get most active
    station_id, station_name, station_count = results.first()

    # Get date ranges for this station's previous year
    results = session.query(func.date(func.max(Measurements.date), '-12 months'), func.max(Measurements.date)).\
        filter(Measurements.station == station_id)
    start_date, finish_date = results.first()

    # Get data for the dates grabbed for this station found
    results = session.query(Measurements.date, Measurements.tobs).\
        filter(Measurements.date >= start_date, Measurements.date <= finish_date).\
        filter(Measurements.station == station_id).\
        order_by(Measurements.date)
    print(results.statement.compile())

    # Build the dictionary list to send back to caller
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    # Close the session we don't want to run out of resources
    session.close()

    return jsonify(tobs_list)


#################################################
# Flask run main app
#################################################
if __name__ == '__main__':
    app.run(debug=True)
