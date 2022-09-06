import os
import json
import sqlite3
import datetime

from aiosqlite import connect
from flask import Flask, redirect, render_template, request
from amadeus import Client, ResponseError, Location
from dotenv import load_dotenv
from helpers import matchAirline, apology

from helpers import matchAirline

app = Flask(__name__)

# if __name__ == '__main__':
#     app.run(debug=True)

app.config["TEMPLATES_AUTO_RELOAD"] = True

app.jinja_env.filters["matchAirline"] = matchAirline

load_dotenv('dotenv.env')

amadeus = Client(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET')
)

print(datetime.datetime.strptime("2021-02-25", "%Y-%m-%d").date())
print(datetime.datetime.today().date())

with sqlite3.connect('airports.db', check_same_thread=False) as con:
    cursor = con.cursor()
    cursor.execute('SELECT code FROM airports3')
    rows = cursor.fetchall()

    airport_codes = []
    for row in rows:
        row = row[0]
        airport_codes.append(row)
        
    for code in airport_codes:
        if None in airport_codes:
            airport_codes.remove(None)      

    countries = []

    cursor2 = con.cursor()
    cursor2.execute('SELECT DISTINCT countryName FROM airports3 ORDER BY countryName')
    countryRows = cursor2.fetchall()

    airport_count = {}

    cursor3 = con.cursor()

    for country in countryRows:
        country = country[0]
        countries.append([country])
        
        cursor3.execute('SELECT COUNT(*) FROM airports3 WHERE countryName = ?', (country,))
        count = cursor3.fetchone()
        airport_count.update({country: count[0]})

    cursor4 = con.cursor()
    cursor4.execute('SELECT countryName, name FROM airports3 ORDER BY countryName')
    result_set = cursor4.fetchall()

    for i, country in enumerate(countries):
        for row in result_set:
            if row[0] == country[0]:
                countries[i].append(row[1])

    for name in countries:
        if None in countries:
            countries.remove(None)

    cursor5 = con.cursor()
    cursor5.execute('SELECT code, name FROM airports')
    codeTranslator = dict(cursor5.fetchall())

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        destination = request.form.get('destination')
        date = request.form.get('date')

        if not destination:
            return apology('Please provide a destination!')

        try:
            datetime.datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return apology('Invalid date format', 403)

        d1 = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        now = datetime.datetime.today().date()
        if d1 < now:
            return apology('Date cannot be in the past', 403)

        with sqlite3.connect('airports.db', check_same_thread=False) as con:
            cursor = con.cursor()
            cursor.execute('SELECT code FROM airports3 WHERE name = ?', (destination,))
            iataCode = cursor.fetchone()
        
        response = []

        for index, code in enumerate(airport_codes):
            if index == 15:
                break
            try:
                flights = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=code,
                    destinationLocationCode=iataCode,
                    departureDate=date,
                    adults='1',
                    max='2'
                ).data

                for entry in flights:
                    fetchedData = amadeus.shopping.flight_offers.pricing.post(entry).data
                    response.append(fetchedData)

            except ResponseError as error:
                print(f"{index}. {error}")

        return render_template('results.html', date=date, destination=destination, response=response, codeTranslator=codeTranslator)

    else:
        return render_template('index.html', countries=countries, airport_count=airport_count)