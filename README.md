# figured out what imports are needed using chat.openai.com

Import the dependencies.
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify
import datetime as dt
import numpy as np

# help from chat.openai.com to figure out that i needed to implement 
Function to find the most active station
Function to calculate `one_year_ago` date

# got the code to calculate the date one year from last date from chat.openai.com
Calculate the date one year from the last date in data set.
most_recent_date = session.query(Measurement.date)\
                 .order_by(Measurement.date.desc()).first()[0]
most_recent_date = dt.datetime.strptime(most_recent_date, '%Y-%m-%d').date()
one_year_ago = most_recent_date - dt.timedelta(days=365)

# assistance from chat.openai.com with group_by and order_by
station_counts = session.query(Measurement.station, func.count(Measurement.station))\
                 .group_by(Measurement.station)\
                 .order_by(func.count(Measurement.station).desc()).all()
