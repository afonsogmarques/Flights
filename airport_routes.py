from amadeus import Client, ResponseError
from dotenv import load_dotenv
import os

load_dotenv('dotenv.env')

amadeus = Client(
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET')
)

try:
    response = amadeus.airport.direct_destinations.get(departureAirportCode='MAD')
    for entry in response.data:
        print(entry["name"])
except ResponseError as error:
    raise error