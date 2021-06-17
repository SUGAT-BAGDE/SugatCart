from flask import Flask, render_template, redirect, make_response, request
from bson.objectid import ObjectId
from flask_pymongo import PyMongo
import pymongo

print("connecting db 1..")
client = pymongo.MongoClient('mongodb+srv://app:db1@sugatcart.helis.mongodb.net/SugatCart?retryWrites=true&w=majority')
database = client["SugatCart"]
products = database["products"]
users = database["users"]
print("connected db 1..")

print("connecting db 2..")
app = Flask(__name__)
app.config["MONGO_URI"] = 'mongodb+srv://app:db1@sugatcart.helis.mongodb.net/SugatCart?retryWrites=true&w=majority'
mongo = PyMongo(app)
print("connected db 2..")

@app.route("/") # root endpoint
def root():
    products_tosend = list(products.find())
    return render_template("index.html", products_tosend=products_tosend), 200

@app.route("/upload_product00", methods=["Get", "POST"]) # to upload product (shhh nobody knows)
def upload_product00():
    if request.method == "POST":
        data = dict(request.form)
        data = {"name":request.form["name"].lower(), "Selling": float(request.form["Selling"]), "off":int(request.form["off"]),"main-cost":float(request.form["main-cost"]),"type":request.form["type"].lower()}
        f = request.files['image']
        a = products.insert_one(data)
        image = a.inserted_id
        mongo.save_file(f"{image}.png", f)
        return redirect("/")
    return render_template("upload.html")

@app.route("/create_Account", methods=["Get", "POST"])
def create_account():
    if request.method == "POST":
        data = dict(request.form)
        try:
            if users.find_one({"email": data["email"]})["email"] == data["email"]:
                return "<h1>Account already exists with this email.</h2><h1><a href=\"/\"> click here to go back</a></h2>"  
        except Exception as e:   
            print(e) 
            data["cart"] = []
            data["total_cart_cost"] = 0
            id = users.insert_one(data).inserted_id
            res = make_response(redirect('/'))
            res.set_cookie("_id", value=f"{id}")
            return res        
    return render_template("create_account.html")

@app.route("/log_in", methods=["Get", "POST"])
def login():  
    if request.method == "POST":
        user = users.find_one({"email":request.form["email"]})
        if user == None:
            return "<h1>No account with this email.</h2><h1><a href=\"/create_Account\">Click here to create</a></h2>"
        if user["password"] == request.form["password"]:
            res = make_response(redirect('/'))
            res.set_cookie("_id", value=f"{user['_id']}")
            return res
    return render_template("login.html")

@app.route("/addtocart=<id>")
def add_to_cart(id):
    user_id = request.cookies.get("_id")
    product_cost = products.find_one({"_id":ObjectId(id)})["Selling"]
    product_id = products.find_one({"_id":ObjectId(id)})["_id"]
    user = dict(users.find_one({"_id" : ObjectId(f"{user_id}")}))
    if len(user["cart"]) == 10:
        return "<h1>You pased limit of items in cart.</h2><h1><a href=\"/\"> click here to go back</a></h2>"
    if ObjectId(f"{product_id}") in user["cart"]:
        return "<h1>Product allready in cart.</h2><h1><a href=\"/\"> click here to go back</a></h2>"
    user["total_cart_cost"] = user["total_cart_cost"] + product_cost
    user["cart"].append(ObjectId(f"{id}"))
    users.update({"_id": ObjectId(user_id)}, {'$set':{"cart":user["cart"], "total_cart_cost":user["total_cart_cost"]}})
    return redirect('/')

@app.route("/mycart")
def mycart():
    items = []
    try:
        user = users.find_one({"_id": ObjectId(request.cookies.get("_id"))})
    except Exception:
        return redirect("/log_in")
    for product_id in user["cart"]:
        items.append(products.find_one({"_id":ObjectId(f"{product_id}")}))
    cost = user["total_cart_cost"]
    return render_template("mycart.html", items=items, cost=cost)

@app.route("/query", methods=["POST"])
def query():
    products_found = []
    if request.form["type"] == "type":
        products_found = list(products.find({"type":request.form["query"].lower()}))
    if request.form["type"] == "name":
        products_found = list(products.find({"name":request.form["query"].lower()}))
    return render_template("query.html", items=products_found)

@app.route('/cheakout')
def cheakout():
    try:        
        id = request.cookies.get("_id")
        user = dict(users.find_one({"_id": ObjectId(f"{id}")}))
    except Exception:
        return redirect('/')
    users.update_one({"_id":ObjectId(f"{id}")}, {"$set" : {"cart": [], "total_cart_cost":float(0)}})
    return redirect('/')


@app.route("/product_view/<id>")
def nkviuh(id):
    return mongo.send_file(id)

if __name__ == '__main__':
    app.run(port=80, debug=True)