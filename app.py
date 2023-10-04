# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, text, func
import pandas as pd
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///C:/Users/morga/OneDrive/Documents/Analysis Projects/archive/Week 10/Starter_Code/Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
Base.prepare(autoload_with=engine)

# reflect the tables
classes = Base.classes.keys()

# Save references to each table
measurement = Base.classes.measurement 
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(bind=engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return(
        f"These are the available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/your_start_date_here><br/>"
        f"/api/v1.0/your_end_date_here><br/>"
        )

@app.route("/api/v1.0/precipitation")
def precip():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prev_year).all()
    session.close()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

@app.route("/api/v1.0/stations")
def stations():
    station_list = session.query(station.station).all()
    session.close()
    stations = list(np.ravel(station_list))
    return jsonify(stations=stations)

@app.route("/api/v1.0/tobs")
def monthly_temp():
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    result = session.query(measurement.tobs).filter(measurement.station == 'USC00519281').filter(measurement.date >= prev_year).all()
    session.close()
    temps = list(np.ravel(result))
    return jsonify(temps=temps)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):

    sel = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    if not end:
        start = dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*sel).filter(measurement.date >= start).all()
        session.close()
        temps = list(np.ravel(results))
        return jsonify(temps=temps)
    
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    results = session.query(*sel).filter(measurement.date >= start).filter(measurement.date <= end).all()
    session.close()
    temps = list(np.ravel(results))
    return jsonify(temps=temps)

if __name__ == "__main__":
    app.run(debug=True)