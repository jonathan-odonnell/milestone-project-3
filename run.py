import os
from flask import Flask, render_template

app = Flask(__name__)


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


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)
