import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)



@app.route("/")
def home():
    return (f"Weather API<br/>"
            f"/api/v1.0/precipitaton<br/>"
            f"/api/v1.0/stations<br/>"
            f"/api/v1.0/tobs<br/>"
            f"/api/v1.0/datesearch/2016-06-25<br/>"
            f"/api/v1.0/datesearch/2015-05-25/2015-07-10<br/>")

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    All = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .order_by(Measurement.date)
                      .all())
    
    Pdata = []
    for result in All:
        precipitation = {result.date: result.prcp, "Station": result.station}
        Pdata.append(precipitation)

    return jsonify(Pdata)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def temperature():

    # Design a query to retrieve the last 12 months of precipitation data and plot the results
    most_recent = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    # Calculate the date 1 year ago from the last data point in the database
    last_year = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date.between
    ('2016-08-23', 'most_recent')).all()
    TData = []
    for r in last_year:
        temperatures = {r.date: r.tobs, "Station": r.station}
        TData.append(temperatures)

    return jsonify(TData)

@app.route('/api/v1.0/datesearch/<startDate>')
def start(startDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .group_by(Measurement.date)
                       .all())

    Tdates = []                       
    for result in results:
        dates = {}
        dates["Date"] = result[0]
        dates["Low Temp"] = result[1]
        dates["Avg Temp"] = result[2]
        dates["High Temp"] = result[3]
        Tdates.append(dates)
    return jsonify(Tdates)

@app.route('/api/v1.0/datesearch/<startDate>/<endDate>')
def startEnd(startDate, endDate):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    moreresults =  (session.query(*sel)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) >= startDate)
                       .filter(func.strftime("%Y-%m-%d", Measurement.date) <= endDate)
                       .group_by(Measurement.date)
                       .all())

    T2dates = []                       
    for result in moreresults:
        dates2 = {}
        dates2["Date"] = result[0]
        dates2["Low Temp"] = result[1]
        dates2["Avg Temp"] = result[2]
        dates2["High Temp"] = result[3]
        T2dates.append(dates2)
    return jsonify(T2dates)

if __name__ == "__main__":
    app.run(debug=True)