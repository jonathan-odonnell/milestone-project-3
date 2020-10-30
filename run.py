import os
from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", page_title="Home")


@app.route("/phones")
def phones():
    return render_template("phones.html", page_title="Phones")


@app.route("/tablets")
def tablets():
    return render_template("tablets.html", page_title="Tablets")


@app.route("/laptops")
def laptops():
    return render_template("laptops.html", page_title="Laptops")


@app.route("/accessories")
def accessories():
    return render_template("accessories.html", page_title="Accessories")


@app.route("/contact")
def contact():
    return render_template("contact.html", page_title="Contact Us")


@app.route("/sign_in")
def sign_in():
    return render_template("sign_in.html", page_title="Sign In")


@app.route("/sign_up")
def sign_up():
    return render_template("sign_up.html", page_title="Sign Up")


@app.route("/profile/<first_name>", methods=["GET", "POST"])
def profile(first_name):
    first_name = session["user"]

    if session["user"]:
        return render_template("profile.html", first_name=first_name)

    return redirect(url_for("sign_in"))


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)
