class MyServer:
    def __init__(self):
        self.favorites = set()
        self.current_restaurant = None
        self.reviews = {}
        self.short_to_official_name = {}

from flask import Flask, request, render_template
import requests

app = Flask(__name__)

my_server = MyServer()

@app.route("/", methods = ["GET", "POST"])
def search_restaurant():
    if my_server.current_restaurant is not None:
        my_server.current_restaurant = False
    return render_template("index.html")

# first opens search-restaurant which opens index. then that takes us to home.html (below) with all the info 

@app.route("/home/", methods = ["GET", "POST"])
def see_result():
    restaurant_name = str(request.args.get("q"))
    URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + restaurant_name + "&inputtype=textquery&key=AIzaSyA_ybZQmfLjIyDVYe70wth69R25CMy9kww"
    data = requests.get(url = URL).json()
    place_id = data["candidates"][0]["place_id"]

    restaurant_info = requests.get(url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + place_id + "&key=AIzaSyA_ybZQmfLjIyDVYe70wth69R25CMy9kww")
    result = restaurant_info.json()["result"]
    name = ""
    formatted_address = ""
    editorial_summary = ""
    overview = ""
    formatted_phone_number = ""
    website = ""
    reservable = ""
    rating = ""
    user_ratings_total = ""
    delivery = ""

    if "name" in result:
        name = result["name"]

    if "formatted_address" in result:
        formatted_address = result["formatted_address"]

    if "editorial_summary" in result:
        editorial_summary = result["editorial_summary"]
        if "overview" in editorial_summary:
            overview = editorial_summary["overview"]

    if "formatted_phone_number" in result:
        formatted_phone_number = result["formatted_phone_number"]

    if "website" in result:
        website = result["website"]

    if "reservable" in result:
        reservable = result["reservable"]
        if reservable == True:
            reservable = "Takes reservations."
        else:
            reservable = "Doesn't take reservations."

    if "rating" in result:
        rating = result["rating"]

    if "user_ratings_total" in result:
        user_ratings_total = result["user_ratings_total"]

    if "delivery" in result:
        delivery = result["delivery"]
        if delivery == True:
            delivery = "Delivers."
        else:
            delivery = "Doesn't deliver."

    my_server.current_restaurant = name
    my_server.short_to_official_name[restaurant_name.lower()] = name
    # creates a dictionary linking the inputted short name to the full name from API

    if request.method == "GET":
        result = request.form
        return render_template("home.html", rest_name = name, address = formatted_address, summary = overview, phone_number = formatted_phone_number, website_link = website, reservations = reservable, ratings = rating, total_ratings = user_ratings_total, makes_deliveries = delivery, result = result)

@app.route("/favorites/", methods = ["GET", "POST"])
def send_to_favorites(): #shows favorites and adds to favorites
    if my_server.current_restaurant is None: #no restaurants to save
        return render_template("favorites.html", favorites = [])
    elif my_server.current_restaurant is not False: #we are saving the restaurant
        my_server.favorites.add(my_server.current_restaurant)
    return render_template("favorites.html", favorites = sorted(list(my_server.favorites)), reviews = my_server.reviews)
    
@app.route("/reviewed/", methods = ["GET", "POST"])
def reviewed(): 
    if request.args.get("review"):
        review = request.args.get("review")
        restname = request.args.get("restname")
        official_name = my_server.short_to_official_name[restname.lower()]
        if official_name not in my_server.reviews:
            my_server.reviews[official_name] = ""
        my_server.reviews[official_name] = review
        return render_template("reviewed.html", review = review, reviews = my_server.reviews)