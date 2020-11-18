import os
from flask import Flask, flash, render_template, redirect, request, session, url_for
from flask_pymongo import PyMongo
from flask_paginate import Pagination, get_page_args
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


def paginate_products(products, offset, per_page):
    return products[offset: offset + per_page]


def paginate(products, page, per_page):
    total = len(products)
    return Pagination(page=page, per_page=per_page, total=total,
                      css_framework='bootstrap4')


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", page_title="Home")


@app.route("/newsletter", methods=["GET", "POST"])
def newsletter():
    mongo.db.newsletter.insert_one(
        {"email": request.form.get("newsletter_sign_up")})
    flash("Thanks for signing up")
    return render_template("index.html", page_title="Home")


@app.route("/search_results", methods=["GET", "POST"])
def search_results():
    session["prev"] = "Search Results"
    if request.method == "POST":
        session["query"] = request.form.get("search")
    products = list(mongo.db.products.find(
        {"$text": {"$search": session["query"]}}).sort("name", 1))
    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page', per_page=4)
    pagination_products = paginate_products(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    return render_template("search_results.html", page_title="Search Results", products=pagination_products, page=page, per_page=per_page, pagination=pagination)


@app.route("/search_results/sort_by/<criteria>")
def sort_by(criteria):
    search = session["query"]
    if criteria == 'a-to-z':
        products = list(mongo.db.products.find(
            {"$text": {"$search": search}}).sort("name", 1))
    elif criteria == 'z-to-a':
        products = list(mongo.db.products.find(
            {"$text": {"$search": search}}).sort("name", -1))
    elif criteria == 'date-added':
        products = list(mongo.db.products.find({"$text": {"$search": search}}).sort(
            [("date_added", -1), ("name", 1)]))
    elif criteria == 'price':
        products = list(mongo.db.products.find({"$text": {"$search": search}}).sort(
            [("price", 1), ("name", 1)]))

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page', per_page=4)
    pagination_products = paginate_products(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    return render_template("search_results.html", page_title="Search Results", products=pagination_products, page=page, per_page=per_page, pagination=pagination)


@app.route("/<category>")
def category_search(category):
    session["prev"] = category.capitalize()
    search = request.args.get("search")
    if search:
        session["query"] = search
        products = list(mongo.db.products.find(
            ({"$text": {"$search": session["query"]}, "category": category})))

    else:
        session["query"] = None
        products = list(mongo.db.products.find({"category": category}))

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page', per_page=4)
    pagination_products = paginate_products(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    return render_template("category_search.html", page_title=category, products=pagination_products, page=page, per_page=per_page, pagination=pagination)


@app.route("/<category>/sort_by/<criteria>")
def category_sort_by(category, criteria):
    if session["query"]:
        if criteria == 'a-to-z':
            products = list(mongo.db.products.find(
                {"$text": {"$search": session["query"]}, "category": category}).sort("name", 1))
        elif criteria == 'z-to-a':
            products = list(mongo.db.products.find(
                {"$text": {"$search": session["query"]}, "category": category}).sort("name", -1))
        elif criteria == 'date-added':
            products = list(mongo.db.products.find({"$text": {"$search": session["query"]}, "category": category}).sort(
                [("date_added", -1), ("name", 1)]))
        elif criteria == 'price':
            products = list(mongo.db.products.find({"$text": {"$search": session["query"]}, "category": category}).sort(
                [("price", 1), ("name", 1)]))

    else:
        if criteria == 'a-to-z':
            products = list(mongo.db.products.find(
                {"category": category}).sort("name", 1))
        elif criteria == 'z-to-a':
            products = list(mongo.db.products.find(
                {"category": category}).sort("name", -1))
        elif criteria == 'date-added':
            products = list(mongo.db.products.find({"category": category}).sort(
                [("date_added", -1), ("name", 1)]))
        elif criteria == 'price':
            products = list(mongo.db.products.find({"category": category}).sort(
                [("price", 1), ("name", 1)]))

    page, per_page, offset = get_page_args(page_parameter='page',
                                           per_page_parameter='per_page', per_page=4)
    pagination_products = paginate_products(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    return render_template("category_search.html", page_title=category, products=pagination_products, page=page, per_page=per_page, pagination=pagination)


@app.route("/review/<product_url>")
def review(product_url):
    product = list(mongo.db.products.find({"url": product_url}))
    page_title = product[0]["name"] + " Review"
    session["product"] = product[0]["name"]
    # https://stackoverflow.com/questions/15974730/how-do-i-get-the-different-parts-of-a-flask-requests-url/15975041#15975041
    session["url"] = request.url
    reviews = list((mongo.db.reviews.find(
        {"product": product[0]["name"]})))
    # https://stackoverflow.com/questions/16920486/average-of-attribute-in-a-list-of-objects
    ratings = []
    ratings.append(int(sum(review["overall_rating"]
                           for review in reviews) / len(reviews)))
    ratings.append(int(sum(review["performance_rating"]
                           for review in reviews) / len(reviews)))
    ratings.append(int(sum(review["battery_rating"]
                           for review in reviews) / len(reviews)))
    ratings.append(int(sum(review["screen_rating"]
                           for review in reviews) / len(reviews)))
    ratings.append(int(sum(review["camera_rating"]
                           for review in reviews) / len(reviews)))
    return render_template("review.html", page_title=page_title, product=product, reviews=reviews, ratings=ratings)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        mongo.db.contact.insert_one(
            {"name": request.form.get("name"), "email": request.form.get("email"), "message": request.form.get("message")})
        flash("Thank you for your message. A member of the team will be in touch shortly.")
    return render_template("contact.html", page_title="Contact Us")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            if check_password_hash(existing_user["password"], request.form.get("password")):
                session["user"] = existing_user["first_name"].lower()
                return redirect(url_for("profile", first_name=session["user"]))
            else:
                flash("Incorrect Email Address and/or Password")
                return redirect(url_for("sign_in"))

        else:
            flash("Incorrect Email Address and/or Password")
            return redirect(url_for("sign_in"))

    return render_template("sign_in.html", page_title="Sign In")


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            flash("Email already registered")
            return redirect(url_for("sign_up"))

        if request.form.get("password") != request.form.get("confirm_password"):
            flash("Passwords do not match")
            return redirect(url_for("sign_up"))

        sign_up = {
            "first_name": request.form.get("first_name").lower(),
            "last_name": request.form.get("last_name").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(sign_up)

        session["user"] = request.form.get("first_name").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", first_name=session["user"]))

    return render_template("sign_up.html", page_title="Sign Up")


@app.route("/profile/<first_name>", methods=["GET", "POST"])
def profile(first_name):
    first_name = session["user"]

    if session["user"]:
        reviews = list((mongo.db.reviews.find(
            {"created_by": session["user"]})))
        return render_template("profile.html", first_name=first_name, page_title="My Account", reviews=reviews)

    return redirect(url_for("sign_in"))


@app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("sign_in"))


@app.route("/reviews/add_review/", methods=["GET", "POST"])
def add_review():
    if request.method == 'POST':
        mongo.db.reviews.insert_one(
            {"overall_rating": int(request.form.get("overall_rating")),
             "performance_rating": int(request.form.get("performance_rating")),
             "battery_rating": int(request.form.get("battery_rating")),
             "screen_rating": int(request.form.get("screen_rating")),
             "camera_rating": int(request.form.get("camera_rating")),
             "review_title": request.form.get("review_title"),
             "review": request.form.get("review"),
             "created_by": session["user"],
             "product": session["product"]
             })
        return redirect(session["url"])
    else:
        return render_template("add_review.html", page_title="Add Review")


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if request.method == 'POST':
        mongo.db.reviews.update({"_id": ObjectId(review_id)},
                                {"overall_rating": int(request.form.get("overall_rating")),
                                 "performance_rating": int(request.form.get("performance_rating")),
                                 "battery_rating": int(request.form.get("battery_rating")),
                                 "screen_rating": int(request.form.get("screen_rating")),
                                 "camera_rating": int(request.form.get("camera_rating")),
                                 "review_title": request.form.get("review_title"),
                                 "review": request.form.get("review"),
                                 "created_by": session["user"],
                                 "product": session["product"]
                                 })
        return redirect(session["url"])
    else:
        review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
        return render_template("edit_review.html", page_title="Edit Review", review=review)


@app.route("/delete_review/<review_id>", methods=["GET", "POST"])
def delete_review(review_id):
    mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})
    return redirect(request.referrer)


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)
