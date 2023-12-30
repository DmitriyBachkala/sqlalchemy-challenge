# Import the dependencies.
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table with the correct case
Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Function to find the most active station
def find_most_active_station(session):
    active_station = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).\
        first()
    return active_station[0] if active_station else None

# Function to calculate `one_year_ago` date
def calculate_one_year_ago(session):
    most_recent_date = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).\
        first()[0]
    most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
    one_year_ago = most_recent_date - dt.timedelta(days=365)
    return one_year_ago

#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt; (use YYYY-MM-DD format)<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt; (use YYYY-MM-DD format)<br/>"
    )

#precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    one_year_ago = calculate_one_year_ago(session)
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago).\
        order_by(Measurement.date).all()
    session.close()

    precipitation_dict = {date: prcp for date, prcp in precipitation_data}
    return jsonify(precipitation_dict)

#stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    station_data = session.query(Station.station).all()
    session.close()

    station_list = [station[0] for station in station_data]
    return jsonify(station_list)

#tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    one_year_ago = calculate_one_year_ago(session)
    most_active_station = find_most_active_station(session)
    temperature_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()

    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in temperature_data]
    return jsonify(temperature_list)

#start
@app.route("/api/v1.0/<start>")
def temperature_start(start):
    session = Session(engine)
    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    temperature_dict = {
        "TMIN": temperature_stats[0][0],
        "TMAX": temperature_stats[0][1],
        "TAVG": temperature_stats[0][2]
    }
    return jsonify(temperature_dict)

#start and end
@app.route("/api/v1.0/<start>/<end>")
def temperature_range(start, end):
    session = Session(engine)
    temperature_stats = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()

    temperature_dict = {
        "TMIN": temperature_stats[0][0],
        "TMAX": temperature_stats[0][1],
        "TAVG": temperature_stats[0][2]
    }
    return jsonify(temperature_dict)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
