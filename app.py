import os
import json
import sqlite3
from aiosqlite import connect
from flask import Flask, redirect, render_template, request
from amadeus import Client, ResponseError
from dotenv import load_dotenv

app = Flask(__name__)

# if __name__ == '__main__':
#     app.run('0.0.0.0')

app.config["TEMPLATES_AUTO_RELOAD"] = True

load_dotenv('dotenv.env')

amadeus = Client(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET')
)

try:
    flights = amadeus.shopping.flight_offers_search.get(
        originLocationCode='MAD',
        destinationLocationCode='FRA',
        departureDate='2022-09-10',
        adults='1'
    ).data

    for entry in flights:
        response = amadeus.shopping.flight_offers.pricing.post(entry).data
        # print(json.dumps(response.data, indent=3))
        numberOfLegs = len(response['flightOffers'][0]['itineraries'][0]['segments'])
        for index in range(numberOfLegs):
            print(response['flightOffers'][0]['itineraries'][0]['segments'][index]['arrival']['iataCode'])

except ResponseError as error:
    print(error)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        destination = request.form.get('destination')
        date = request.form.get('date')

        try:
            flights = amadeus.shopping.flight_offers_search.get(
                originLocationCode='MAD',
                destinationLocationCode='FRA',
                departureDate='2022-09-10',
                adults='1'
            ).data

            response = []
            for entry in flights:
                response.append(amadeus.shopping.flight_offers.pricing.post(entry).data)
                # print(json.dumps(response.data, indent=3)
                # print(entry)

        except ResponseError as error:
            print(error)

        return render_template('results.html', date=date, destination=destination, response=response)

    else:
        with sqlite3.connect('airports.db', check_same_thread=False) as con:
            cursor = con.cursor()
            cursor.execute('SELECT name FROM airports ORDER BY name')
            rows = cursor.fetchall()

            airport_names = []
            for row in rows:
                row = row[0]
                airport_names.append(row)
                
            for name in airport_names:
                if None in airport_names:
                    airport_names.remove(None)
            return render_template('index.html', airport_names=airport_names)

# @app.route('/search')
# def search():
    
#     # check prices
#     try:
#         flights = amadeus.shopping.flight_offers_search.get(
#             originLocationCode='LON',
#             destinationLocationCode='PAR',
#             departureDate='2022-12-05',
#             adults='1',
#             max='5'
#         ).data

#         response = []
#         for entry in flights:
#             response.append(amadeus.shopping.flight_offers.pricing.post(entry).data)
#             # print(json.dumps(response.data, indent=3)
        
#     except ResponseError as error:
#         print(error)

#     return render_template('search.html', response=response)