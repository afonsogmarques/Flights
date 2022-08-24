import os
import json

from flask import Flask, redirect, render_template, request
from amadeus import Client, ResponseError
from dotenv import load_dotenv

app = Flask(__name__)

# if __name__ == '__main__':
#     app.run(host='0.0.0.0')

app.config["TEMPLATES_AUTO_RELOAD"] = True

load_dotenv('dotenv.env')

amadeus = Client(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET')
)

# try:
#     response = amadeus.airport.direct_destinations.get(departureAirportCode='MAD')
#     for entry in response.data:
#         print(entry["name"], entry["iataCode"])
# except ResponseError as error:
#     print(error)


# flights = amadeus.shopping.flight_offers_search.get(
#     originLocationCode='LON',
#     destinationLocationCode='PAR',
#     departureDate='2022-12-05',
#     adults='1',
#     max='5'
# ).data

# response = []
# for entry in flights:
#     response.append(amadeus.shopping.flight_offers.pricing.post(entry).data)
#     print(json.dumps(response, indent=3))

@app.route('/')
def index():
    
    # check prices
    try:
        flights = amadeus.shopping.flight_offers_search.get(
            originLocationCode='LON',
            destinationLocationCode='PAR',
            departureDate='2022-12-05',
            adults='1',
            max='5'
        ).data

        response = []
        for entry in flights:
            response.append(amadeus.shopping.flight_offers.pricing.post(entry).data)
            # print(json.dumps(response.data, indent=3)
        
    except ResponseError as error:
        print(error)

    return render_template('index.html', response=response)