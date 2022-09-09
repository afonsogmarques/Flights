import os
from amadeus import Client, ResponseError
from dotenv import load_dotenv
from flask import redirect, render_template, request, session
from datetime import date

load_dotenv('dotenv.env')

amadeus = Client(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET')
)

def matchAirline(airline_code):
    try:
        airline_name = amadeus.reference_data.airlines.get(airlineCodes=airline_code).data
        return airline_name[0]['commonName']
    except ResponseError:
        return airline_code

def apology(message):
    """Render message as an apology to user."""
    return render_template("apology.html", message=message)


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
