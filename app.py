import os
import json
import sqlite3
from aiosqlite import connect
from flask import Flask, redirect, render_template, request
from amadeus import Client, ResponseError
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
    cursor.execute('SELECT name FROM amadeus_airports ORDER BY name')
    rows = cursor.fetchall()

    airport_names = []
    for row in rows:
        row = row[0]
        airport_names.append(row)
        
    for name in airport_names:
        if None in airport_names:
            airport_names.remove(None)
    
    # for index, name in enumerate(airport_names):
    #     try:
    #         airport = amadeus.reference_data.locations.get(keyword=name, subType="AIRPORT")
    #         if len(airport.data) == 0:
    #             continue
    #         else:
    #             print(f"{index}. {name}")
    #             cursor.execute('INSERT OR IGNORE INTO amadeus_airports SELECT * FROM airports WHERE name = ?', (name,))
    #     except ResponseError as error:
    #         print(f"error {error}")

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        destination = request.form.get('destination')
        date = request.form.get('date')

        response = []

        try:
            airport = amadeus.reference_data.locations.get(keyword=destination, subType="AIRPORT")
            if len(airport.data) == 0:
                print("Airport doesn't exist")

            else:
                iataCode = airport.data[0]["iataCode"]

                for index, row in enumerate(airport_names):
                    try:
                        airport2 = amadeus.reference_data.locations.get(keyword=row, subType="AIRPORT")
                        if len(airport2.data) == 0:
                            print(f"{index}. {row} doesn't exist.")
                            # if index == 30:
                            #     break
                            continue

                        else:
                            print(f"{index}. {row} exists")
                            try:
                                flights = amadeus.shopping.flight_offers_search.get(
                                    originLocationCode=airport2.data[0]["iataCode"],
                                    destinationLocationCode=iataCode,
                                    departureDate=date,
                                    adults='1',
                                    max='3'
                                ).data

                                for entry in flights:
                                    fetchedData = amadeus.shopping.flight_offers.pricing.post(entry).data
                                    response.append(fetchedData)
                                    # print(json.dumps(response.data, indent=3)
                                    # print(entry)

                            except ResponseError as error:
                                print(f"{index}. {error}")
                            
                    except ResponseError as error:
                        print(f"{index}. {error}")

        except ResponseError as error:
            print(error)

        return render_template('results.html', date=date, destination=destination, response=response)

    else:
        return render_template('index.html', airport_names=airport_names)