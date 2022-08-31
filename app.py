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

# try:
#     test = amadeus.reference_data.locations.get(keyword='LIS', subType='AIRPORT')
#     print(json.dumps(test.data, indent=3))
# except ResponseError as error:
#     print(f"error {error}")

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

    cursor2 = con.cursor()
    cursor2.execute('SELECT name FROM airports3 ORDER BY name')
    nameRows = cursor2.fetchall()

    airport_names = []
    for row in nameRows:
        row = row[0]
        airport_names.append(row)

    for name in airport_names:
        if None in airport_names:
            airport_names.remove(None)

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
            print(iataCode[0])
        
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
        return render_template('index.html', airport_codes=airport_names)