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


current_product = ""


current_search = {}


previous_urls = []


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


def add_rating(productRating, newUserRating, totalProductRatings):
    rating = ((productRating * (totalProductRatings - 1)) +
              float(newUserRating)) / totalProductRatings
    rating = round(rating, 1)
    return rating


def edit_rating(productRating, oldUserRating, newUserRating, totalProductRatings):
    rating = ((productRating * totalProductRatings) -
              oldUserRating + float(newUserRating)) / totalProductRatings
    rating = round(rating, 1)
    return rating


def delete_rating(productRating, newUserRating, totalProductRatings):
    rating = ((productRating * (totalProductRatings + 1)) -
              float(newUserRating)) / totalProductRatings
    rating = round(rating, 1)
    return rating


def add_star_rating(star_rating, prev_ratings, new_ratings):
    if star_rating == 1:
        new_ratings['one_star'] = prev_ratings[0]['one_star'] + 1
    if star_rating == 2:
        new_ratings['two_stars'] = prev_ratings[0]['two_stars'] + 1
    if star_rating == 3:
        new_ratings['three_stars'] = prev_ratings[0]['three_stars'] + 1
    if star_rating == 4:
        new_ratings['four_stars'] = prev_ratings[0]['four_stars'] + 1
    if star_rating == 5:
        new_ratings['five_stars'] = prev_ratings[0]['five_stars'] + 1


def remove_star_rating(star_rating, prev_ratings, new_ratings):
    if star_rating == 1:
        new_ratings['one_star'] = prev_ratings[0]['one_star'] - 1
    if star_rating == 2:
        new_ratings['two_stars'] = prev_ratings[0]['two_stars'] - 1
    if star_rating == 3:
        new_ratings['three_stars'] = prev_ratings[0]['three_stars'] - 1
    if star_rating == 4:
        new_ratings['four_stars'] = prev_ratings[0]['four_stars'] - 1
    if star_rating == 5:
        new_ratings['five_stars'] = prev_ratings[0]['five_stars'] - 1


@app.before_request
def save_url():
    #https://stackoverflow.com/questions/18891373/url-history-in-flask-application
    # https://stackoverflow.com/questions/15974730/how-do-i-get-the-different-parts-of-a-flask-requests-url/15975041#15975041
    if (len(previous_urls) == 3):
        del previous_urls[0]
        previous_urls.append(request.url)
    else:
        previous_urls.append(request.url)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", page_title="Home")


@app.route("/newsletter", methods=["GET", "POST"])
def newsletter():
    mongo.db.newsletter.insert_one(
        {"email": request.form.get("newsletter_sign_up")})
    flash("Thanks for signing up to our newsletter", "info")
    return render_template("index.html", page_title="Home")


@app.route("/reviews")
def reviews():
    current_search["type"] = "Reviews"
    current_search["url"] = request.url
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
    current_search["type"] = category.capitalize()
    current_search["url"] = request.url
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
    global current_product
    current_product = product[0]["name"]
    reviews = list((mongo.db.reviews.find(
        {"product": product[0]["name"]})))
    dates = []
    for review in reviews:
        dates.append(review["date_added"].strftime("%d %B %Y"))
    return render_template("review.html", 
        page_title=page_title, 
        current_search=current_search, 
        product=product, 
        reviews=reviews, 
        dates=dates)


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
                session["user"] = existing_user["first_name"] + \
                    " " + existing_user["last_name"]
                session["user_type"] = existing_user["user_type"]
                flash("Login Successful", "success")
                return redirect(previous_urls[0])
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

        if request.form.get('password') != request.form.get('confirm_password'):
            flash("Passwords do not match", "error")
            return redirect(url_for('sign_up'))

        sign_up = {
            "first_name": request.form.get("first_name").lower(),
            "last_name": request.form.get("last_name").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(sign_up)

        session["user"] = request.form.get(
            "first_name") + " " + request.form.get(
            "last_name")
        flash("Registration Successful!", "success")
        return redirect(previous_urls[0])

    return render_template("sign_up.html", page_title="Sign Up")


@ app.route("/product_management", methods=["GET", "POST"])
def product_management():
    if session["user_type"] == "admin":
        products = list(mongo.db.products.find().sort('name', 1))
        page, per_page, offset = get_page_args(
            page_parameter='page', per_page_parameter='per_page', per_page=10)
        pagination_products = paginate_products(products, offset, per_page)
        pagination = paginate(products, page, per_page)
        return render_template("product_management.html", page_title="Product Management", products=pagination_products, pagination=pagination)

    else:
        flash("You do not have permission to view this page", "error")
        return redirect(request.referrer)


@ app.route("/logout")
def logout():
    flash("Logout Successful", "success")
    session.pop("user")
    return redirect(request.referrer)


@ app.route("/reviews/add_review/", methods=["GET", "POST"])
def add_review():
    if request.method == 'POST':
        mongo.db.reviews.insert_one({
            'overall_rating': int(request.form.get('overall_rating')),
            'performance_rating': int(request.form.get('performance_rating')),
            'usability_rating': int(request.form.get('usability_rating')),
            'quality_rating': int(request.form.get('quality_rating')),
            'price_rating': int(request.form.get('price_rating')),
            'review_title': request.form.get('review_title'),
            'review': request.form.get('review'),
            'date_added': datetime.datetime.now(),
            'created_by': session['user'],
            'product': current_product,
        })

        product_count = mongo.db.reviews.count({"product": current_product})

        product_ratings = list(mongo.db.products.find({"name": current_product}, {"overall_rating": 1, "performance_rating": 1,
        "usability_rating": 1, "price_rating": 1, "quality_rating": 1,
        "one_star": 1, "two_stars": 1, "three_stars": 1, "four_stars": 1,
        "five_stars": 1, "_id": 0}))

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

        add_star_rating(int(request.form.get('overall_rating')),
                        product_ratings, new_ratings)

        mongo.db.products.update_one(
            {'name': current_product}, {"$set": new_ratings})

        return redirect(previous_urls[0])
    else:
        return render_template("add_review.html", page_title="Add Review")


@ app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    if request.method == 'POST':
        product_count = mongo.db.reviews.count({"product": current_product})

        product_ratings = list(mongo.db.products.find({"name": current_product}, {"overall_rating": 1, "performance_rating": 1,
        "usability_rating": 1, "price_rating": 1, "quality_rating": 1,
        "one_star": 1, "two_stars": 1, "three_stars": 1, "four_stars": 1,
        "five_stars": 1, "_id": 0}))

        user_ratings = list(mongo.db.reviews.find({"_id": ObjectId(review_id)},
        {"overall_rating": 1, "performance_rating": 1, "usability_rating": 1,
        "price_rating": 1, "quality_rating": 1, "_id": 0}))

        mongo.db.reviews.update({'_id': ObjectId(review_id)}, {
            'overall_rating': int(request.form.get('overall_rating')),
            'performance_rating': int(request.form.get('performance_rating')),
            'usability_rating': int(request.form.get('usability_rating')),
            'quality_rating': int(request.form.get('quality_rating')),
            'price_rating': int(request.form.get('price_rating')),
            'review_title': request.form.get('review_title'),
            'review': request.form.get('review'),
            'date_added': datetime.datetime.now(),
            'created_by': session['user'],
            'product': current_product,
        })

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

        if (int(request.form.get('overall_rating')) != user_ratings[0]['overall_rating']):
            add_star_rating(int(request.form.get('overall_rating')),
                            product_ratings, new_ratings)
            remove_star_rating(
                user_ratings[0]['overall_rating'], product_ratings, new_ratings)

        mongo.db.products.update_one(
            {'name': current_product}, {"$set": new_ratings})

        return redirect(previous_urls[0])

    else:
        review = mongo.db.reviews.find_one({'_id': ObjectId(review_id)})

        return render_template('edit_review.html', page_title='Edit Review',
                               review=review)


@ app.route("/delete_review/<review_id>", methods=["GET", "POST"])
def delete_review(review_id):

    product_count = mongo.db.reviews.count({"product": current_product})

    product_ratings = list(mongo.db.products.find({"name": current_product}, {"overall_rating": 1, "performance_rating": 1,
    "usability_rating": 1, "price_rating": 1, "quality_rating": 1,
    "one_star": 1, "two_stars": 1, "three_stars": 1, "four_stars": 1,
    "five_stars": 1, "_id": 0}))

    user_ratings = list(mongo.db.reviews.find({"_id": ObjectId(review_id)},
    {"overall_rating": 1, "performance_rating": 1, "usability_rating": 1,
    "price_rating": 1, "quality_rating": 1, "_id": 0}))

    mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})

    new_ratings = {
            'overall_rating': delete_rating(product_ratings[0]
            ['overall_rating'], user_ratings[0]['overall_rating'],
            product_count), 'performance_rating': delete_rating
            (product_ratings[0]['performance_rating'], user_ratings[0]
            ['performance_rating'], product_count), 'usability_rating':
            delete_rating(product_ratings[0]['usability_rating'],
            user_ratings[0]['usability_rating'], product_count), 
            'price_rating': delete_rating(product_ratings[0]
            ['price_rating'], user_ratings[0]['price_rating'], 
            product_count), 'quality_rating': delete_rating(product_ratings
            [0]['quality_rating'], user_ratings[0]['quality_rating'], 
            product_count),
        }

    remove_star_rating(
                user_ratings[0]['overall_rating'], product_ratings, new_ratings)

    mongo.db.products.update_one(
            {'name': current_product}, {"$set": new_ratings})

    return redirect(previous_urls[0])


@ app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        if session["user_type"] == "admin":
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
                "camera and video": request.form.get('camera_video'),
                "battery life": request.form.get('battery'),
                "connectivity": request.form.get('connectivity'),
                "additional features": request.form.get('additional_features'),
            }

            keys = list(product.keys())

            for key in keys:
                if product[key] == "":
                    del product[key]

            print(product)

            mongo.db.products.insert_one(product)

            return redirect(url_for('product_management'))

        else:
            flash("You do not have permission to view this page", "error")
            return redirect(request.referrer)

    return render_template('add_product.html', page_title='Add Product')


@ app.route("/edit_product/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    if request.method == "POST":
        if session["user_type"] == "admin":
            product = {
                "name": request.form.get('name'),
                "category": request.form.get('category'),
                "price": int(request.form.get('price')),
                "brand": request.form.get('brand'),
                "image_url": request.form.get('image-url'),
                "image_alt": request.form.get('image-alt'),
                "colours": request.form.get('colours'),
                "capacity": request.form.get('capacity'),
                "display": request.form.get('display'),
                "processor_memory_graphics": request.form.get('processor_memory_graphics'),
                "camera_video": request.form.get('camera_video'),
                "battery": request.form.get('battery'),
                "connectivity": request.form.get('connectivity'),
                "additional_features": request.form.get('additional_features'),
            }
            keys = list(product.keys())
            for key in keys:
                if product[key] == "":
                    del product[key]
            mongo.db.products.update_one(
                {'_id': ObjectId(product_id)}, {"$set": product})
            return redirect(url_for('product_management'))

        else:
            flash("You do not have permission to view this page", "error")
            return redirect(request.referrer)

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
def delete_product(product_id):
    if session["user_type"] == "admin":
        mongo.db.products.delete_one({"_id": ObjectId(product_id)})
        return redirect(url_for('product_management'))

    else:
        flash("You do not have permission to view this page", "error")
        return redirect(request.referrer)


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)
