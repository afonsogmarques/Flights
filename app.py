import os
import json
import sqlite3
from aiosqlite import connect
from flask import Flask, redirect, render_template, request
from amadeus import Client, ResponseError, Location
from dotenv import load_dotenv

app = Flask(__name__)

# if __name__ == '__main__':
#     app.run(debug=True)

app.config["TEMPLATES_AUTO_RELOAD"] = True

load_dotenv('dotenv.env')

amadeus = Client(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET')
)

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

    cursor.close()

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
    
    airport_list = {}

    cursor4 = con.cursor()
    cursor4.execute('SELECT countryName, name FROM airports3 ORDER BY countryName')
    result_set = cursor4.fetchall()

    for i, country in enumerate(countries):
        print(country[0])
        for row in result_set:
            if row[0] == country[0]:
                countries[i].append(row[1])

    for country in countries:
        print(country)

    print()
    print(airport_count)

    for name in countries:
        if None in countries:
            countries.remove(None)


    cursor2.close()
    
    # for index, code in enumerate(airport_codes):
    #     try:
    #         airport = amadeus.reference_data.locations.get(keyword=code, subType="AIRPORT")
    #         if len(airport.data) == 0:
    #             continue
    #         else: 
    #             print(f"{index}. {code}")
    #             cursor.execute('INSERT OR IGNORE INTO amadeus_airports4 SELECT * FROM airports WHERE code = ?', (code,))
    #     except ResponseError as error:
    #         print(f"error {error}")

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        destination = request.form.get('destination')
        date = request.form.get('date')

        with sqlite3.connect('airports.db', check_same_thread=False) as con:
            cursor = con.cursor()
            cursor.execute('SELECT code FROM airports3 WHERE name = ?', (destination,))
            iataCode = cursor.fetchone()
        
        response = []

        for index, code in enumerate(airport_codes):
            try:
                airport2 = amadeus.reference_data.locations.get(keyword=code, subType="AIRPORT,CITY")
                
                if len(airport2.data) == 0:
                    continue

                else:
                    try:
                        flights = amadeus.shopping.flight_offers_search.get(
                            originLocationCode=airport2.data[0]["iataCode"],
                            destinationLocationCode=iataCode,
                            departureDate=date,
                            adults='1',
                            max='5'
                        ).data

                        for entry in flights:
                            fetchedData = amadeus.shopping.flight_offers.pricing.post(entry).data
                            response.append(fetchedData)

                    except ResponseError as error:
                        print(f"{index}. {error}")
                    
            except ResponseError as error:
                print(f"{index}. {error}")

        return render_template('results.html', date=date, destination=destination, response=response)

    else:
        return render_template('index.html', countries=countries, airport_count=airport_count)