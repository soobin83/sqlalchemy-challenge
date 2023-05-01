# Import the dependencies.
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        f"Welcome to the homepage.<br/>"
        f"Available routes:<br/>"
        f"Precipitation in one year: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Temperature in one year: /api/v1.0/tobs<br/>"
        f"Min, Max, Avg temperature on a date(YYYY-MM-DD): /api/v1.0/temp/<start><br/>"
        f"Min, Max, Avg temperature for duration from start date to end date(YYYY-MM-DD/YYYY-MM-DD): /api/v1.0/temp/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    one_year_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    session.close()
    precipitation = {date:prcp for date,prcp in one_year_data}
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    results = session.query((Station.station)).all()
    session.close()
    stations = list(np.ravel(results))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temperatures():
    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    results = session.query(Measurement.tobs).filter(Measurement.station=='USC00519281').filter(Measurement.date >= one_year_ago).all()
    session.close()
    temperatures = list(np.ravel(results))
    return jsonify(temperatures)


@app.route("/api/v1.0/temp/<start>")
def stats(start=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # calculate TMIN, TAVG, TMAX for dates greater than start
    results = session.query(*sel).\
        filter(Measurement.date >= start).all()
    session.close()
        # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>/<end>")
def statsend(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""
    # Select statement
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    # Unravel results into a 1D array and convert to a list
    temps = list(np.ravel(results))
    return jsonify(temps)

if __name__ == "__main__":
    app.run(debug=True)
