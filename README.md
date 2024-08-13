# iFlights :airplane:
#### :clapper: Video Demo: 
<https://www.youtube.com/watch?v=67DduhPebOU&ab_channel=AfonsoMarques> 
####
#### :computer: Live Demo: 
<https://iflights.onrender.com/> [ For guaranteed results, pick Copenhagen airport. Results can take long to load, but they do. :) ]
#### 
#### :memo: Description:

iFlights is a **"reverse" flight search engine** that should ultimately allow the user to browse all scheduled flights to a provided destination (here restricted to European airports for performance's sake) on a provided date, as well as their price, not from a single selected departure location but from **all of the available ones**, sorted from cheapest to most expensive.

The idea came from this issue I experienced while traveling abroad. At one point in my trip I needed to return home, so I began searching for flights on popular travel search engines such as Skyscanner, Kiwi, and the like. The problem I faced while using these services - and the gap I think still needs to be filled - was that I was **forced to insert my departure airport no matter what**. This might sound crazy, because you’d usually know where you’d be flying from. However, on some occasions, and provided that time is not of importance to you, it turns out to be much more inexpensive to fly from a neighbour town or country where you could very cheaply get to by bus or some other means of land transportation.

This web-app fetches data from an external API developed by Amadeus, which I credit on every page, and makes use of Python and Flask to store such data, along with **Jinja templating**, **HTML**, **CSS** and **Bootstrap** to display it to the user. Furthermore, it makes use of some **Javascript** for certain interactions such as sending data to the back-end through **AJAX requests**, as well as redirecting to Skyscanner’s website or app with certain parameters.

On top of this, the user is also able to register on a persistent **SQL database**, and, when logged in, has the ability to save his favourite flights on his personal account, as well as removing them, case they’re no longer of interest.

The file **app.py** is the brain of the operation, where I set up all the necessary configurations to be able to run flask as well as the Amadeus Client in order to be able to make calls to their API. It is also in this file that all of the logic happens, from registering the user, to logging in, logging out, retrieving an airport list from the database, catching input errors, and rendering specific pages with the necessary data.
Alongside app.py, I have also written **helpers.py**, where some reusable helper functions were implemented and directly imported to app.py as mere functions, or even Jinja filters to later be used in the HTML templates that required them.
I made use of several libraries that helped me accomplish my goals with this project, such as **werkzeug.security** for hashing passwords, **datetime** for easy time variable management, **sqlite3** for SQL operations, amongst many others...


Unfortunately, the free version of the Amadeus API only provides outdated or mock-data, which means that iFlights does not have any real utility, at least not yet. However, if you would still like giving it a go, it is live at:
<https://iflights.onrender.com/>