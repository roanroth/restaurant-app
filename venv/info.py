class MyServer:
    def __init__(self):
        self.favorites = set()
        self.current_restaurant = None

from flask import Flask, request, render_template
import requests

app = Flask(__name__)

my_server = MyServer()

@app.route("/", methods = ["GET", "POST"])
def search_restaurant():
    return render_template("index.html")

# first opens search-restaurant which opens index. then that takes us to home.html (below) with all the info 

@app.route("/home/", methods = ["GET", "POST"])
def see_result():
    q = request.args.get("q")
    restaurant_name = str(q)
    URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=" + restaurant_name + "&inputtype=textquery&key=AIzaSyA_ybZQmfLjIyDVYe70wth69R25CMy9kww"
    r = requests.get(url = URL)
    data = r.json()
    candidates = data["candidates"]
    place_id_object = candidates[0]
    place_id = place_id_object["place_id"]

    restaurant_info = requests.get(url = "https://maps.googleapis.com/maps/api/place/details/json?place_id=" + place_id + "&key=AIzaSyA_ybZQmfLjIyDVYe70wth69R25CMy9kww")
    details = restaurant_info.json()
    result = details["result"]
    formatted_data = {}
    if "name" in result:
        name = result["name"]
        formatted_data["name: "] = name
        print(name)
    else:
        name = ""

    if "formatted_address" in result:
        formatted_address = result["formatted_address"]
        formatted_data["formatted address: "] = formatted_address
        print(formatted_address)
    else:
        formatted_address = ""

    if "editorial_summary" in result:
        editorial_summary = result["editorial_summary"]
        if "overview" in editorial_summary:
            overview = editorial_summary["overview"]
            formatted_data["restaurant overview: "] = overview
            print(overview)
        else:
            overview = ""
    else:
        overview = ""

    if "formatted_phone_number" in result:
        formatted_phone_number = result["formatted_phone_number"]
        formatted_data["phone number: "] = formatted_phone_number
        print(formatted_phone_number)
    else:
        formatted_phone_number = ""

    if "website" in result:
        website = result["website"]
        formatted_data["website: "] = website
        print(website)
    else:
        website = ""

    if "reservable" in result:
        reservable = result["reservable"]
        if reservable == True:
            reservable = "Takes reservations."
            formatted_data["Takes reservations."] = ""
        else:
            reservable = "Doesn't take reservations."
            formatted_data["Doesn't take reservations."] = ""
        print(reservable)
    else:
        reservable = ""

    if "rating" in result:
        rating = result["rating"]
        formatted_data["rating: "] = rating
        print(rating)
    else:
        rating = ""

    if "user_ratings_total" in result:
        user_ratings_total = result["user_ratings_total"]
        formatted_data["Rating: "] = user_ratings_total
        print(user_ratings_total)
    else:
        user_ratings_total = ""

    if "delivery" in result:
        delivery = result["delivery"]
        if delivery == True:
            delivery = "Delivers."
            formatted_data["delivers."] = ""
        else:
            delivery = "Doesn't deliver."
            formatted_data["doesn't deliver."] = ""
        print(delivery)
    else:
        delivery = ""

    my_server.current_restaurant = name

    if request.method == "GET":
        result = request.form
        return render_template("home.html", restaurant_name = name, address = formatted_address, summary = overview, phone_number = formatted_phone_number, website_link = website, reservations = reservable, ratings = rating, total_ratings = user_ratings_total, makes_deliveries = delivery, result = result)


@app.route("/favorites/", methods = ["GET", "POST"])
def send_to_favorites():
    no_favorites = ["No restaurants in Favorites."]
    if my_server.current_restaurant is None:
        return render_template("favorites.html", favorites = no_favorites)
    else:
        my_server.favorites.add(my_server.current_restaurant)
        return render_template("favorites.html", favorites = my_server.favorites)
    # when we click see favorites from home page after looking up a restaurant but not adding to favorites, it is added to favorites regardless
    