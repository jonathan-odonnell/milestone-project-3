import os
from functools import wraps
from flask import (Flask, flash, jsonify, render_template,
                   redirect, request, session, url_for)
from flask_pymongo import PyMongo
from flask_paginate import get_page_args
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
if os.path.exists("env.py"):
    import env

from utils import paginate_products, paginate, get_price_range, add_rating,edit_rating, delete_rating, star_rating, sort_items, product_ratings_query, user_ratings_query

app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)

# https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Please sign in to view this page", "error")
            return redirect(url_for('sign_in'))
        elif session['user']['user_type'] != "admin":
            flash("Sorry, you do not have permission to view this page", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", page_title="Home")


@app.route("/newsletter", methods=["POST"])
def newsletter():
    mongo.db.newsletter.insert_one(
        {"email": request.form.get("email")})
    return jsonify({"success": True})


@app.route('/reviews')
@app.route("/reviews/<category>")
def reviews(category="all"):
    search = request.args.get("search")
    brands = request.args.get("brands")
    price = request.args.get("price")
    sortBy = request.args.get("sort")
    query = {}
    order_by = []
    page_title = "Reviews"

    if category != "all":
        page_title = category.capitalize()

    if search:
        query["$text"] = {"$search": search}

        if category != "all":
            query["category"] = category

    elif not search:
        query["category"] = category

    if sortBy:
        order_by = sort_items(sortBy)

    elif not sortBy:
        order_by = [("name", 1)]

    if brands:
        brands = brands.split(",")
        if len(brands) == 1:
            query["brand"] = brands[0]

        else:
            query["brand"] = {"$in": brands}

    if price:
        price = int(price)
        price_Query = get_price_range(category, price)
        query["price"] = price_Query

    print(query)

    products = list(mongo.db.products.find(query).sort(order_by))

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
    current_user = None
    if "user" in session:
        current_user = session['user']['first_name'] + " " + session['user']['last_name']
    reviews = list((mongo.db.reviews.find(
        {"product": product[0]["name"]})))
    dates = []
    total_reviews = product[0]['one_star'] + product[0]['two_stars'] + product[0]['three_stars'] + product[0]['four_stars'] + product[0]['five_stars']
    for review in reviews:
        dates.append(review["date_added"].strftime("%d %B %Y"))
    return render_template("review_details.html", 
        page_title=page_title, 
        product=product, 
        reviews=reviews, 
        dates=dates,
        total_reviews=total_reviews,
        current_user=current_user)

@app.route("/up_vote", methods=["GET", "POST"])
def up_vote():
    #https://stackoverflow.com/questions/36620864/passing-variables-from-flask-back-to-ajax
    #https://stackoverflow.com/questions/26079754/flask-how-to-return-a-success-status-code-for-ajax-call/26080784#26080784
    review_id = review_id = request.form.get('review_id')
    mongo.db.reviews.update_one(
        {'_id': ObjectId(review_id)}, {"$inc": {"up_vote": 1}})
    up_vote = list(mongo.db.reviews.find({"_id": ObjectId(review_id)},
    {"up_vote": 1, "_id": 0}))

    return jsonify({"up_vote": up_vote[0]['up_vote'], "success": True})

@app.route("/down_vote", methods=["GET", "POST"])
def down_vote():
    #https://stackoverflow.com/questions/36620864/passing-variables-from-flask-back-to-ajax
    #https://stackoverflow.com/questions/26079754/flask-how-to-return-a-success-status-code-for-ajax-call/26080784#26080784
    review_id = request.form.get('review_id')
    mongo.db.reviews.update_one(
        {'_id': ObjectId(review_id)}, {"$inc": {"down_vote": 1}})
    down_vote = list(mongo.db.reviews.find({"_id": ObjectId(review_id)},
    {"down_vote": 1, "_id": 0}))

    return jsonify({"down_vote": down_vote[0]['down_vote'], "success": True})

@ app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        mongo.db.contact.insert_one({'name': request.form.get('name'),
                                     'email': request.form.get('email'),
                                     'message': request.form.get('message')})
        flash('Thank you for your message. A member of the team will be in touch shortly.', category='info')
    return render_template("contact.html", page_title="Contact Us")


@ app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            if check_password_hash(existing_user["password"],
                                   request.form.get("password")):
                session["user"] = {
                    "first_name": existing_user["first_name"],
                    "last_name": existing_user["last_name"],
                    "email": existing_user["email"],
                    "user_type": existing_user["user_type"]
                }
                flash("Login Successful", "success")
                return redirect(request.form.get("next"))
            else:
                flash("Incorrect Email Address and/or Password", "error")
                return redirect(url_for("sign_in"))

        else:
            flash("Incorrect Email Address and/or Password", "error")
            return redirect(url_for("sign_in"))

    return render_template("sign_in.html", page_title="Sign In")


@ app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            flash("Email already registered", "error")
            return redirect(url_for("sign_up"))

        sign_up = {
            "first_name": request.form.get("first_name").lower(),
            "last_name": request.form.get("last_name").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password")),
            "user_type": "standard"
        }
        mongo.db.users.insert_one(sign_up)

        session["user"] = {
            "first_name": request.form.get(
            "first_name"),
            "last_name": request.form.get(
            "first_name"),
            "email": request.form.get(
            "email"),
            "user_type": request.form.get(
            "user_type")
        }

        if request.form.get("newsletter_signup") == "on":
            mongo.db.newsletter.insert_one(
                {"email": request.form.get("email")})

        flash("Registration Successful!", "success")
        return redirect(request.form.get("next"))

    return render_template("sign_up.html", page_title="Sign Up")


@ app.route("/product_management", methods=["GET", "POST"])
@login_required
def product_management():
    sort_by = request.args.get("sort")

    if sort_by:
        products = list(mongo.db.products.find().sort(sort_items(sort_by)))

    else:
        products = list(mongo.db.products.find().sort('name', 1))

    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=10)
    pagination_products = paginate_products(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    return render_template("product_management.html", page_title="Product Management", products=pagination_products, pagination=pagination)


@ app.route("/logout")
def logout():
    flash("Logout Successful", "success")
    session.pop("user")
    return redirect(url_for('sign_in'))


@ app.route("/reviews/add_review/", methods=["GET", "POST"])
@login_required
def add_review():
    if request.method == 'POST':
        product_count = mongo.db.reviews.count({"product": request.form.get('product')})

        product_ratings = list(mongo.db.products.find({"name": request.form.get('product')}, product_ratings_query()))

        new_ratings = {
            'overall_rating': add_rating(product_ratings[0]
            ['overall_rating'], request.form.get('overall_rating'),
            product_count), 'performance_rating': add_rating
            (product_ratings[0]['performance_rating'], request.form.get
            ('performance_rating'), product_count), 'usability_rating':
            add_rating(product_ratings[0]['usability_rating'],
            request.form.get('usability_rating'), product_count),
            'price_rating': add_rating(product_ratings[0]['price_rating'],
            request.form.get('price_rating'), product_count),
            'quality_rating': add_rating(product_ratings[0]
            ['quality_rating'], request.form.get('quality_rating'),
            product_count),
        }

        mongo.db.products.update_one(
            {'name': request.form.get('product')}, {"$set": new_ratings})

        mongo.db.products.update_one({'name': request.form.get('product')}, star_rating(new_rating=int(request.form.get('overall_rating'))))

        mongo.db.reviews.insert_one({
            'overall_rating': int(request.form.get('overall_rating')),
            'performance_rating': int(request.form.get('performance_rating')),
            'usability_rating': int(request.form.get('usability_rating')),
            'quality_rating': int(request.form.get('quality_rating')),
            'price_rating': int(request.form.get('price_rating')),
            'review_title': request.form.get('review_title'),
            'review': request.form.get('review'),
            'date_added': datetime.datetime.now(),
            'created_by': session['user']['first_name'] + " " + session['user']['last_name'],
            'product': request.form.get('product'),
        })

        return redirect(request.form.get('next'))
    else:
        return render_template("add_review.html", page_title="Add Review")


@ app.route("/edit_review/<review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    if request.method == 'POST':
        user_ratings = list(mongo.db.reviews.find({'_id': ObjectId(review_id)}, user_ratings_query()))

        product_ratings = list(mongo.db.products.find({"name": user_ratings[0]['product']}, product_ratings_query()))

        product_count = mongo.db.reviews.count({"product": user_ratings[0]['product']})

        new_ratings = {
            'overall_rating': edit_rating(product_ratings[0]
            ['overall_rating'], user_ratings[0]['overall_rating'],
            request.form.get('overall_rating'), product_count),
            'performance_rating': edit_rating(product_ratings[0]
            ['performance_rating'], user_ratings[0]['performance_rating'],
            request.form.get('performance_rating'), product_count),
            'usability_rating': edit_rating(product_ratings[0]
            ['usability_rating'], user_ratings[0]['usability_rating'],
            request.form.get('usability_rating'), product_count),
            'price_rating': edit_rating(product_ratings[0]
            ['price_rating'], user_ratings[0]['price_rating'], 
            request.form.get('price_rating'), product_count),
            'quality_rating': edit_rating(product_ratings[0]
            ['quality_rating'], user_ratings[0]['quality_rating'],
            request.form.get('quality_rating'), product_count),
        }

        mongo.db.products.update_one(
            {'name': request.form.get('product')}, {"$set": new_ratings})

        if (int(request.form.get('overall_rating')) != user_ratings[0]['overall_rating']):
            mongo.db.products.update_one({"_id": review_id}, star_rating(request.form.get('overall_rating'), user_ratings[0]['overall_review']))
        
        mongo.db.reviews.update_one({'_id': ObjectId(review_id)}, {"$set": {
            'overall_rating': int(request.form.get('overall_rating')),
            'performance_rating': int(request.form.get('performance_rating')),
            'usability_rating': int(request.form.get('usability_rating')),
            'quality_rating': int(request.form.get('quality_rating')),
            'price_rating': int(request.form.get('price_rating')),
            'review_title': request.form.get('review_title'),
            'review': request.form.get('review'),
            'date_added': datetime.datetime.now(),
        }})

        return redirect(request.form.get('next'))

    else:
        review = mongo.db.reviews.find_one({'_id': ObjectId(review_id)})

        return render_template('edit_review.html', page_title='Edit Review',
                               review=review)


@ app.route("/delete_review/<review_id>", methods=["GET", "POST"])
@login_required
def delete_review(review_id):
    user_ratings = list(mongo.db.reviews.find({'_id': ObjectId(review_id)}, user_ratings_query()))

    product_ratings = list(mongo.db.products.find({"name": user_ratings[0]['product']}, product_ratings_query()))

    product_count = mongo.db.reviews.count_documents({"product": user_ratings[0]['product']})

    new_ratings = {
            'overall_rating': delete_rating(product_ratings[0]
            ['overall_rating'], user_ratings[0]['overall_rating'],
            product_count), 'performance_rating': delete_rating
            (product_ratings[0]['performance_rating'], user_ratings[0]
            ['performance_rating'], product_count), 'usability_rating':
            delete_rating(product_ratings[0]['usability_rating'],
            user_ratings[0]['usability_rating'], product_count), 
            'price_rating': delete_rating(product_ratings
            [0]['price_rating'], user_ratings[0]['price_rating'], 
            product_count), 'quality_rating': delete_rating(product_ratings[0]
            ['quality_rating'], user_ratings[0]['quality_rating'], 
            product_count)
        }

    mongo.db.products.update_one(
            {'name': request.form.get('product')}, {"$set": new_ratings})

    mongo.db.products.update_one({"name": user_ratings[0]['product']}, star_rating(prev_rating=user_ratings[0]['overall_rating']))

    mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})

    return redirect(request.referrer)


@ app.route("/add_product", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        product = {
            "name": request.form.get('name'),
            "category": request.form.get('category'),
            "price": int(request.form.get('price')),
            "brand": request.form.get('brand'),
            "image_url": request.form.get('image-url'),
            "image_alt": request.form.get('image-alt'),
            "date_added": datetime.datetime.now(),
            "colours": request.form.get('colours'),
            "capacity": request.form.get('capacity'),
            "display": request.form.get('display'),
            "processor, memory and graphics": request.form.get('processor_memory_graphics'),
            "camera and video": request.form.get('camera-video'),
            "battery life": request.form.get('battery'),
            "connectivity": request.form.get('connectivity'),
            "additional features": request.form.get('additional-features'),
        }

        keys = list(product.keys())
        # this part does something
        for key in keys:
            if product[key] == "":
                del product[key]

        mongo.db.products.insert_one(product)

        return redirect(url_for('product_management'))

    return render_template('add_product.html', page_title='Add Product')


@ app.route("/edit_product/<product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    if request.method == "POST":
        product = {
            "name": request.form.get('name'),
            "category": request.form.get('category'),
            "price": int(request.form.get('price')),
            "brand": request.form.get('brand'),
            "image_url": request.form.get('image-url'),
            "image_alt": request.form.get('image-alt'),                "colours": request.form.get('colours'),
            "capacity": request.form.get('capacity'),
            "display": request.form.get('display'),
            "processor_memory_graphics": request.form.get('processor-memory-graphics'),
            "camera_video": request.form.get('camera-video'),
            "battery": request.form.get('battery'),
            "connectivity": request.form.get('connectivity'),
            "additional_features": request.form.get('additional-features'),
        }
        keys = list(product.keys())
        for key in keys:
            if product[key] == "":
                del product[key]
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)}, {"$set": product})
        return redirect(url_for('product_management'))

    else:
        product = mongo.db.products.find_one({'_id': ObjectId(product_id)})
        categories = mongo.db.categories.find()
        return render_template(
            'edit_product.html',
            page_title='Edit Product',
            categories=categories,
            product=product
        )


@ app.route("/delete_product/<product_id>", methods=["GET", "POST"])
@login_required
def delete_product(product_id):
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    return redirect(url_for('product_management'))


@app.errorhandler(404)
def page_not_found(e):
    """
    Redirects the user back to the home page 
    if the HTTP request returns a 404 page not found error is returned.
    Code is from https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
    """
    return redirect(url_for('index'))


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)
