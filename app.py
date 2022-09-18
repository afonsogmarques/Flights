import os
import json
import sqlite3
import datetime

from aiosqlite import connect
from flask import Flask, redirect, render_template, request, session
from amadeus import Client, ResponseError
from dotenv import load_dotenv
from helpers import matchAirline, apology, add_years, login_required
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

if __name__ == '__main__':
    app.run(debug=True)

app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.jinja_env.filters["matchAirline"] = matchAirline

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

# HOMEPAGE
@app.route('/', methods=['GET', 'POST'])
def index():

    with sqlite3.connect('airports.db', check_same_thread=False) as con:
        cursor5 = con.cursor()
        cursor5.execute('SELECT code, name FROM airports')
        session["codeTranslator"] = dict(cursor5.fetchall())

    if request.method == 'POST':
        session["destination"] = request.form.get('destination')
        session["date"] = request.form.get('date')

        if not session["destination"]:
            return apology('Please select a destination!')
        elif not session["date"]:
            return apology('Please select a date!')

        try:
            datetime.datetime.strptime(session["date"], "%Y-%m-%d")
        except ValueError:
            return apology('Invalid date format')

        d1 = datetime.datetime.strptime(session["date"], "%Y-%m-%d").date()
        now = datetime.datetime.today().date()

        if d1 < now:
            return apology('Date cannot be in the past!')
        elif d1 > add_years(now, 1):
            return apology('Latest possible travel date is one year from today!')

        with sqlite3.connect('airports.db', check_same_thread=False) as con:
            cursor = con.cursor()
            cursor.execute('SELECT code FROM airports3 WHERE name = ?', (session["destination"],))
            iataCode = cursor.fetchone()
        
        session["response"] = []

        for index, code in enumerate(airport_codes):
            if index == 10:
                break
            try:
                flights = amadeus.shopping.flight_offers_search.get(
                    originLocationCode=code,
                    destinationLocationCode=iataCode,
                    departureDate=session["date"],
                    adults='1',
                    max='1'
                ).data

                for entry in flights:
                    fetchedData = amadeus.shopping.flight_offers.pricing.post(entry).data
                    session["response"].append(fetchedData)

            except ResponseError as error:
                print(error)

        return redirect('/results')

    else:
        user_id = session.get("user_id")

        if user_id == None:
            return render_template('index.html', countries=countries, airport_count=airport_count)
        else:
            with sqlite3.connect("airports.db", check_same_thread=False) as con:
                cursor = con.cursor()
                username = cursor.execute('SELECT username FROM users WHERE id = ?', (session["user_id"],)).fetchone()
            return render_template('index.html', countries=countries, airport_count=airport_count, username=username[0].capitalize())


# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    with sqlite3.connect('airports.db', check_same_thread=False) as con:
        cursor = con.cursor()
        users = cursor.execute('SELECT username FROM users')

        if request.method == 'POST':
            username = request.form.get('username')
            if not username:
                return apology('Please provide a username!')

            password = request.form.get('password')
            if not password:
                return apology('Please provide a password!')

            confirmation = request.form.get('confirmation')
            if not confirmation or confirmation != password:
                return apology("Passwords don't match!")

            for user in users:
                if username == user:
                    return apology('Username is already in use!')
            
            sql = "INSERT INTO users (username, hash) VALUES (?, ?)"
            values = username, generate_password_hash(password)
            cursor.execute(sql, values)

            return redirect('/')
        else:
            return render_template('register.html')


@app.route("/login", methods=['GET', 'POST'])
def login():

    session.clear()

    if request.method == 'POST':
        
        if not request.form.get('username'):
            return apology('Must provide username!')

        if not request.form.get('password'):
            return apology('Must provide password!')

        with sqlite3.connect('airports.db', check_same_thread=False) as con:
            cursor = con.cursor()
            users = cursor.execute('SELECT * FROM users WHERE username = ?', (request.form.get('username'),)).fetchall()

        if len(users) != 1 or not check_password_hash(users[0][2], request.form.get("password")):
            return apology("Invalid username and/or password!")
        
        session["user_id"] = users[0][0]

        return redirect("/")

    else:
        return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
    

@app.route("/favorites", methods=['POST', 'GET'])
@login_required
def favorites():
    with sqlite3.connect('airports.db', check_same_thread=False) as con:
        cursor = con.cursor()
        if request.method == "POST":
            data = request.get_json()
            cursor.execute("DELETE FROM favorites WHERE id = ?;", (data["id"],))

            return redirect("/favorites")

        else:
            favorites = cursor.execute("SELECT * FROM favorites WHERE user_id = ?", (session["user_id"],)).fetchall()
            return render_template('favorites.html', favorites=favorites)


@app.route("/results", methods=['GET', 'POST'])
def results():

    with sqlite3.connect('airports.db', check_same_thread=False) as con:
        if request.method == 'POST':
            data = request.get_json()

            number_of_legs = len(data["carriers"]) - 1
            cursor = con.cursor()
            
            if number_of_legs == 0:
                sql = 'INSERT INTO favorites (departureCode, departureName, departureTime, itineraryType, arrivalTime, arrivalCode, arrivalName, totalPrice, carrierName, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
                values = data["departureCode"], data["departureName"], data["departureTime"], data["itineraryType"], data["arrivalTime"], data["arrivalCode"], data["arrivalName"], data["totalPrice"], data["carriers"][0], session["user_id"]
                cursor.execute(sql, values)

            elif number_of_legs == 1:
                sql = 'INSERT INTO favorites (departureCode, departureName, departureTime, itineraryType, arrivalTime, arrivalCode, arrivalName, totalPrice, carrierName, carrierName1, legDepartureTime1, legDestinationCode1, legDestinationName1, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
                values = data["departureCode"], data["departureName"], data["departureTime"], data["itineraryType"], data["arrivalTime"], data["arrivalCode"], data["arrivalName"], data["totalPrice"], data["carriers"][0], data["carriers"][1], data["legDepartureTimes"][0], data["legDestinationCodes"][0], data["legDestinationNames"][0], session["user_id"]
                cursor.execute(sql, values)

            elif number_of_legs == 2:
                sql = 'INSERT INTO favorites (departureCode, departureName, departureTime, itineraryType, arrivalTime, arrivalCode, arrivalName, totalPrice, carrierName, carrierName1, legDepartureTime1, legDestinationCode1, legDestinationName1, carrierName2, legDepartureTime2, legDestinationCode2, legDestinationName2, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);'
                values = data["departureCode"], data["departureName"], data["departureTime"], data["itineraryType"], data["arrivalTime"], data["arrivalCode"], data["arrivalName"], data["totalPrice"], data["carriers"][0], data["carriers"][1], data["legDepartureTimes"][0], data["legDestinationCodes"][0], data["legDestinationNames"][0], data["carriers"][2], data["legDepartureTimes"][1], data["legDestinationCodes"][1], data["legDestinationNames"][1], session["user_id"]
                cursor.execute(sql, values)
                
            return ("", 204)

        else:
            return render_template('results.html', date=session.get("date", None), destination=session.get("destination", None), response=session.get("response", None), codeTranslator=session.get("codeTranslator", None))