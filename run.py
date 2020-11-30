import os
from flask import (Flask, flash, render_template,
                   redirect, request, session, url_for)
from flask_pymongo import PyMongo
from flask_paginate import Pagination, get_page_args
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
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
    return Pagination(
        page=page,
        per_page=per_page,
        total=total,
        css_framework='bootstrap4'
    )


def sortItems(sort):
    if sort == "a-to-z":
        sortQuery = {"name": 1}
        return sortQuery
    elif sort == "z-to-a":
        sortQuery = {"name": -1}
        return sortQuery
    elif sort == "date-added":
        sortQuery = {"date_added": -1, "name": 1}
        return sortQuery
    elif sort == "price":
        sortQuery = {"price": -1, "name": 1}
        return sortQuery


def getPriceRange(category, value):
    if category == "phones":
        if value == 1:
            query = {"$gte": 0, "$lte": 500}
            return query
        elif value == 2:
            query = {"$gte": 500, "$lte": 750}
            return query
        elif value == 3:
            query = {"$gte": 750, "$lte": 1000}
            return query
        elif value == 4:
            query = {"$gte": 1000}
            return query
    if category == "tablets":
        if value == 1:
            query = {"$gte": 0, "$lte": 500}
            return query
        elif value == 2:
            query = {"$gte": 500, "$lte": 750}
            return query
        elif value == 3:
            query = {"$gte": 750, "$lte": 1000}
            return query
        elif value == 4:
            query = {"$gte": 1000}
            return query
    if category == "laptops":
        if value == 1:
            query = {"$gte": 0, "$lte": 750}
            return query
        elif value == 2:
            query = {"$gte": 750, "$lte": 1000}
            return query
        elif value == 3:
            query = {"$gte": 1000, "$lte": 1250}
            return query
        elif value == 4:
            query = {"$gte": 1250, "$lte": 1500}
            return query
        elif value == 5:
            query = {"$gte": 1500}
            return query
    if category == "accessories":
        if value == 1:
            query = {"$gte": 0, "$lte": 200}
            return query
        elif value == 2:
            query = {"$gte": 200, "$lte": 300}
            return query
        elif value == 3:
            query = {"$gte": 300, "$lte": 400}
            return query
        elif value == 4:
            query = {"$gte": 400}
            return query
    if category == "all":
        if value == 1:
            query = {"$gte": 0, "$lte": 250}
            return query
        elif value == 2:
            query = {"$gte": 250, "$lte": 500}
            return query
        elif value == 3:
            query = {"$gte": 500, "$lte": 750}
            return query
        elif value == 4:
            query = {"$gte": 750, "$lte": 1000}
            return query
        elif value == 5:
            query = {"$gte": 1000}
            return query


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


@app.route("/reviews")
def reviews():
    session["prev"] = "Reviews"
    search = request.args.get("search")
    categories = request.args.get("categories")
    brands = request.args.get("brands")
    price = request.args.get("price")
    sortBy = request.args.get("sort")
    query = []

    if search:
        if categories:
            categories = categories.split(",")
            query.append({'$match': {'$text': {'$search': search},
                                     'category': {'$in': categories}}})

        if not categories:
            query.append(
                {"$match": {"$text": {"$search": search}}})

        if sortBy:
            sortQuery = sortItems(sortBy)
            query.append({"$sort": sortQuery})

        if not sortBy:
            query.append({"$sort": {"name": 1}})

        if brands:
            brands = brands.split(",")
            query[0]["$match"]["brand"] = {"$in": brands}

        if price:
            price = int(price)
            price_Query = getPriceRange("all", price)
            query[0]["$match"]["price"] = price_Query

    if query:
        products = list(mongo.db.products.aggregate(query))

    else:
        products = None

    total = len(products)

    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=6)
    pagination_products = paginate_products(products, offset, per_page)
    pagination = paginate(products, page, per_page)
    record_numbers = pagination.info[48:53]
    pagination_info = "Displaying {} of {} reviews found for".format(
        record_numbers, total)

    return render_template(
        'reviews.html',
        page_title='Reviews',
        selected_categories=categories,
        selected_price=price,
        selected_brands=brands,
        products=pagination_products,
        search=search,
        pagination_info=pagination_info,
        page=page,
        per_page=per_page,
        pagination=pagination,
    )


@app.route("/reviews/<category>")
def category_reviews(category):
    page_title = category.capitalize()
    session["prev"] = category.capitalize()
    search = request.args.get("search")
    brands = request.args.get("brands")
    price = request.args.get("price")
    sortBy = request.args.get("sort")
    query = []

    if search:
        query.append(
            {"$match": {"$text": {"$search": search}, "category": category}})

    elif not search:
        query.append(
            {"$match": {"category": category}})

    if sortBy:
        sortQuery = sortItems(sortBy)
        query.append({"$sort": sortQuery})

    elif not sortBy:
        query.append({"$sort": {"name": 1}})

    if brands:
        brands = brands.split(",")

        if len(brands) == 1:
            query[0]["$match"]["brand"] = brands[0]

        else:
            query[0]["$match"]["brand"] = {"$in": brands}

    if price:
        price = int(price)
        price_Query = getPriceRange(category, price)
        query[0]["$match"]["price"] = price_Query

    products = list(mongo.db.products.aggregate(query))

    total = len(products)

    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=6)
    pagination_products = paginate_products(products, offset, per_page)
    pagination = paginate(products, page, per_page)
    record_numbers = pagination.info[48:53]
    pagination_info = "Displaying {} of {} reviews".format(
        record_numbers, total)

    return render_template(
        "reviews.html",
        page_title=page_title,
        selected_brands=brands,
        selected_price=price,
        products=pagination_products,
        pagination_info=pagination_info,
        total=total,
        page=page,
        per_page=per_page,
        pagination=pagination
    )


@ app.route("/review_details/<product_id>")
def review_details(product_id):
    product = list(mongo.db.products.find({"_id": ObjectId(product_id)}))
    page_title = product[0]["name"] + " Review"
    session["product"] = product[0]["name"]
    # https://stackoverflow.com/questions/15974730/how-do-i-get-the-different-parts-of-a-flask-requests-url/15975041#15975041
    session["url"] = request.url
    reviews = list((mongo.db.reviews.find(
        {"product": product[0]["name"]})))
    dates = []
    for review in reviews:
        dates.append(review["date_added"].strftime("%d %B %Y"))
    return render_template("review.html", page_title=page_title,
                           product=product, reviews=reviews, dates=dates)


@ app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        mongo.db.contact.insert_one({'name': request.form.get('name'),
                                     'email': request.form.get('email'),
                                     'message': request.form.get('message')})
        flash('Thank you for your message. A member of the team will be in touch shortly.')
    return render_template("contact.html", page_title="Contact Us")


@ app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            if check_password_hash(existing_user["password"],
                                   request.form.get("password")):
                session["user"] = existing_user["first_name"].lower()
                return redirect(url_for("profile", first_name=session["user"]))
            else:
                flash("Incorrect Email Address and/or Password")
                return redirect(url_for("sign_in"))

        else:
            flash("Incorrect Email Address and/or Password")
            return redirect(url_for("sign_in"))

    return render_template("sign_in.html", page_title="Sign In")


@ app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            flash("Email already registered")
            return redirect(url_for("sign_up"))

        if request.form.get('password') != request.form.get('confirm_password'):
            flash('Passwords do not match')
            return redirect(url_for('sign_up'))

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


@ app.route("/profile/<first_name>", methods=["GET", "POST"])
def profile(first_name):
    first_name = session["user"]

    if session["user"]:
        reviews = list((mongo.db.reviews.find(
            {"created_by": session["user"]})))
        return render_template("profile.html", first_name=first_name,
                               page_title="My Account", reviews=reviews)

    return redirect(url_for("sign_in"))


@ app.route("/logout")
def logout():
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("sign_in"))


@ app.route("/reviews/add_review/", methods=["GET", "POST"])
def add_review():
    if request.method == 'POST':
        mongo.db.reviews.insert_one({
            'overall_rating': int(request.form.get('overall_rating')),
            'performance_rating': int(request.form.get('performance_rating')),
            'battery_rating': int(request.form.get('battery_rating')),
            'screen_rating': int(request.form.get('screen_rating')),
            'camera_rating': int(request.form.get('camera_rating')),
            'review_title': request.form.get('review_title'),
            'review': request.form.get('review'),
            'date_added': datetime.datetime.now(),
            'created_by': session['user'],
            'product': session['product'],
        })
        return redirect(session["url"])
    else:
        return render_template("add_review.html", page_title="Add Review")


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if request.method == 'POST':
        mongo.db.reviews.update({'_id': ObjectId(review_id)}, {
            'overall_rating': int(request.form.get('overall_rating')),
            'performance_rating': int(request.form.get('performance_rating')),
            'battery_rating': int(request.form.get('battery_rating')),
            'screen_rating': int(request.form.get('screen_rating')),
            'camera_rating': int(request.form.get('camera_rating')),
            'review_title': request.form.get('review_title'),
            'review': request.form.get('review'),
            'date_added': datetime.datetime.now(),
            'created_by': session['user'],
            'product': session['product'],
        })
        return redirect(session['url'])
    else:
        review = mongo.db.reviews.find_one({'_id': ObjectId(review_id)})
        return render_template('edit_review.html', page_title='Edit Review',
                               review=review)


@ app.route("/delete_review/<review_id>", methods=["GET", "POST"])
def delete_review(review_id):
    mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})
    return redirect(request.referrer)


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)
