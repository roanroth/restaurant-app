class MyServer:
    def __init__(self):
        self.favorites = set()
        self.current_restaurant = None
        self.id_to_reviews = {}
        self.short_to_official_name = {}
        self.id_to_name = {}

from flask import Flask, redirect, request, render_template
import requests

app = Flask(__name__)

port = 8080

my_server = MyServer()

@app.route("/", methods = ["GET", "POST"])
def search_restaurant():
    if my_server.current_restaurant is not None:
        my_server.current_restaurant = False
    return render_template("index.html")

@app.route("/home/", methods = ["GET", "POST"])
def see_result():
    restaurant_name = str(request.args.get("q"))
    if not restaurant_name:
        return redirect("/")

    URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + restaurant_name + "%20restaurant%20new%20york&inputtype=textquery&key=AIzaSyA_ybZQmfLjIyDVYe70wth69R25CMy9kww"
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
    else:
        formatted_phone_number = "No phone number listed."

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


    my_server.current_restaurant = place_id 
    my_server.id_to_name[place_id] = name
    # creates a dictionary linking the inputted short name to the full name from API

    if request.method == "GET":
        result = request.form
        return render_template("home.html", rest_name = name, address = formatted_address, summary = overview, phone_number = formatted_phone_number, website_link = website, reservations = reservable, ratings = rating, total_ratings = user_ratings_total, makes_deliveries = delivery, result = result)
    
def removeSpace(s): 
    return s.replace(" ", "")

def format(s):
    return s.replace(" ", "_").lower()

@app.route("/favorites/", methods = ["GET", "POST"])
def send_to_favorites(): #shows favorites and adds to favorites
    if my_server.current_restaurant is None: #no restaurants to save
        return render_template("favorites.html", favorites = [])
    elif my_server.current_restaurant is not False: #we are saving the restaurant
        my_server.favorites.add(my_server.current_restaurant)
    return render_template("favorites.html", favorites = my_server.favorites, names = my_server.id_to_name, reviews = my_server.id_to_reviews)
    
@app.route("/reviewed/", methods = ["GET", "POST"])
def reviewed(): 
    if request.args.get("review"):
        review = request.args.get("review")
        restaurant_id = request.args.get("restname")

        official_name = my_server.id_to_name[restaurant_id]

        if official_name not in my_server.id_to_reviews:
            my_server.id_to_reviews[official_name] = ""

        my_server.id_to_reviews[restaurant_id] = review

        return render_template("reviewed.html", review = review, reviews = my_server.id_to_reviews)
    else:
        return redirect("/favorites/")
    
if __name__ == "__main__":
   app.run(port=port)