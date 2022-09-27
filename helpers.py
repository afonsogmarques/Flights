import os
from amadeus import Client, ResponseError
from dotenv import load_dotenv
from flask import redirect, render_template, request, session
from datetime import date
from functools import wraps

load_dotenv('dotenv.env')

amadeus = Client(
    client_id="5FjS2AkleL500ZgIjiGYPW0Q7e64QRDA",
    client_secret="UlAsiAmfOHwdPEPF"
)


def matchAirline(airline_code):
    try:
        airline_name = amadeus.reference_data.airlines.get(airlineCodes=airline_code).data
        return airline_name[0]['commonName']
    except ResponseError:
        return airline_code


def add_years(d, years):
    # By Gareth Rees in https://stackoverflow.com/questions/15741618/add-one-year-in-current-date-python
    
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))


#Require Login
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def skyscanner_date_fromatter(date):
    new_date = date.replace("-", "");
    skyscanner_date = new_date[2:8];

    return skyscanner_date

