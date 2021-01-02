import os
import datetime
from functools import wraps
from flask import (Flask, flash, jsonify, render_template,
                   redirect, request, session, url_for, abort)
from flask_pymongo import PyMongo
from flask_paginate import get_page_args
from bson.objectid import ObjectId
from bson.decimal128 import Decimal128
from werkzeug.security import generate_password_hash, check_password_hash
from utils import (add_ratings, create_user_session, delete_ratings,
                   edit_ratings, paginate, paginate_items,
                   product_ratings_query, search, sort_items, star_rating,
                   user_ratings_query)

if os.path.exists("env.py"):
    import env


app = Flask(__name__)


app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


def login_required(f):
    """
    A wrapper to prevent users who are not signed in from accessing the page
    and redirects to the sign in page. Code is from https://
    flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/ and https://
    blog.tecladocode.com/handling-the-next-url-when-logging-in-with-flask/ and
    https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Please sign in to view this page", "error")
            return redirect(url_for('sign_in', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    A wrapper to prevent users who are not admins from accessing the page and
    returns a status of 403. Code is from https://flask.palletsprojects.com/en/
    1.1.x/ patterns/viewdecorators/ and https://flask.palletsprojects.com/en/
    1.1.x/ patterns/errorpages/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['user']['user_type'] != "admin":
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    """ A view to return the index page """
    return render_template("index.html", page_title="Home")


@app.route("/newsletter", methods=["POST"])
def newsletter():
    """
    A view to add the email to the newsletters database and return a success
    status. Code is from https://stackoverflow.com/questions/
    26079754/ flask-how-to-return-a-success-status-code-for-ajax-call/
    26080784#26080784
    """
    mongo.db.newsletter.insert_one(
        {"email": request.form.get("email")})
    return jsonify(success=True)


@app.route('/reviews')
@app.route("/reviews/<category>")
def reviews(category="All"):
    """
    A view to return all reviews which satisfy the search criteria, including
    sorting, filters and search queries.
    """

    """
    Redirects to the home page if the search is a search query and the URL
    does not contain a search query. Search Parameters code is from https://
    www.kite.com/python/answers/
    how-to-get-parameters-from-a-url-using-flask-in-python
    """
    if category == "All" and not request.args.get('search'):
        flash("You didn't enter any search criteria!", "error")
        return redirect(url_for('index'))

    # Converts the search perameters to a dictionary

    search_params = request.args.to_dict()

    # Adds the category for category searches to the search_perams dictionary

    if category != "All":
        search_params['categories'] = category

    # Gets the query dictionary

    query = search(search_params, category)

    # Sets the page title

    page_title = category

    if category == "All":
        page_title = "Reviews"

    """
    Gets the products which match the search criteria from the database and
    sorts them. Code for the sort method is from https://docs.mongodb.com/
    manual/reference/method/cursor.sort/index.html
    """
    products = list(mongo.db.products.find(query).sort(
        sort_items(request.args.get("sort"))))

    """
    Gets the filters from the database. Code for returning selected fields from
    https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/
    """
    if category == "All":
        filters = list(mongo.db.categories.find({}, {"name": 1, "_id": 0}))

    else:
        filters = mongo.db.categories.find_one(
            {"name": category}, {"brands": 1, "prices": 1, "_id": 0})

    # Gets the number of products in the products list

    total = len(products)

    """
    Paginates the products. Code is from https://gist.github.com/mozillazg/
    69fb40067ae6d80386e10e105e6803c9
    """
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=6)
    pagination_products = paginate_items(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    """
    Generates pagination info. Code is adapted from
    https://pythonhosted.org/Flask-paginate/
    """
    record_numbers = pagination.info[48:53]

    if category == "All":
        pagination_info = 'Displaying {} of {} reviews found for "{}"'.format(
            record_numbers, total, search_params['search'])
    else:
        pagination_info = 'Displaying {} of {} reviews'.format(
            record_numbers, total)

    return render_template(
        "reviews.html",
        page_title=page_title,
        filters=filters,
        selected_category=search_params.get('categories'),
        selected_brands=search_params.get('brands'),
        selected_price=search_params.get('price'),
        products=pagination_products,
        pagination_info=pagination_info,
        total=total,
        page=page,
        per_page=per_page,
        pagination=pagination
    )


@app.route("/review_details/<product_id>")
def review_details(product_id):
    """
    A view to return the product's specifications, ratings and reviews.
    """

    # Gets the product's specifications from the database
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})

    # Sets the page title
    page_title = product["name"] + " Review"

    # Sets the current user if there is a user logged in
    if session('user'):
        current_user = "{} {}".format(session['user']['first_name'],
                                      session['user']['last_name'])

    """
    Gets the product's reviews from the database and sorts them. Code for the
    sort method is from https://docs.mongodb.com/manual/reference/method/
    cursor.sort/index.html
    """
    reviews = list((mongo.db.reviews.find(
        {"product": product["name"]})).sort("date_added", -1))

    """
    Updates the date_added value in the review dictionary to be
    in the correct format. Code is from https://www.w3schools.com/python/
    python_datetime.asp
    """
    for review in reviews:
        review['date_added'] = review['date_added'].strftime("%d %B %Y")

    return render_template("review_details.html",
                           page_title=page_title,
                           product=product,
                           reviews=reviews,
                           current_user=current_user)


@app.route("/up_vote", methods=["POST"])
def up_vote():
    """
    A view to increases the up vote value by one and return the updated total
    and a success status.
    """
    review_id = review_id = request.form.get('review_id')

    """
    Code for incrementing the up_vote value by 1 is from https://
    docs.mongodb.com/manual/reference/operator/update/inc/
    """
    mongo.db.reviews.update_one(
        {'_id': ObjectId(review_id)}, {"$inc": {"up_vote": 1}})

    """
    Code for returning only specified fields from the database is from
    https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/
    """
    up_vote = mongo.db.reviews.find_one({"_id": ObjectId(review_id)},
                                        {"up_vote": 1, "_id": 0})

    """
    Code for returning a success status is from https://stackoverflow.com/
    questions/26079754/flask-how-to-return-a-success-status-code-for-ajax-call/
    26080784#26080784
    """
    return jsonify({"up_vote": up_vote['up_vote'], "success": True})


@app.route("/down_vote", methods=["POST"])
def down_vote():
    """
    A view to increases the down vote value by one and return the updated total
    and a success status.
    """
    review_id = request.form.get('review_id')

    """
    Code for incrementing the down_vote value by 1 is from https://
    docs.mongodb.com/manual/reference/operator/update/inc/
    """
    mongo.db.reviews.update_one(
        {'_id': ObjectId(review_id)}, {"$inc": {"down_vote": 1}})

    """
    Code for returning only specified fields from the database is from
    https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/
    """
    down_vote = mongo.db.reviews.find_one({"_id": ObjectId(review_id)},
                                          {"down_vote": 1, "_id": 0})

    """
    Code for returning a success status is from https://stackoverflow.com/
    questions/26079754/flask-how-to-return-a-success-status-code-for-ajax-call/
    26080784#26080784
    """
    return jsonify({"down_vote": down_vote['down_vote'], "success": True})


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """
    A view to return the contact page and post the data inputted into the
    contact form to the contact database.
    """
    if request.method == "POST":
        mongo.db.contact.insert_one(request.form.to_dict())

        """
        Code for returning a success status is from https://stackoverflow.com/
        questions/26079754/
        flask-how-to-return-a-success-status-code-for-ajax-call/
        26080784#26080784
        """
        return jsonify(success=True)

    return render_template("contact.html", page_title="Contact Us")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    """
    A view to return the sign in page, and if the request method is post,
    verify that the email address and password inputted are correct and sign
    the user in.
    """
    if request.method == "POST":
        """
        Gets the next search perameter from the URL. Code is from https://
        blog.tecladocode.com/handling-the-next-url-when-logging-in-with-flask/
        """
        next_url = request.form.get('next')

        # Checks if the email entered already exists in the database.
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            if check_password_hash(existing_user["password"],
                                   request.form.get("password")):
                """
                If the user exists, ensure hashed password matches user input.
                Code for message categories is from https://
                flask.palletsprojects.com/en/1.1.x/patterns/flashing/
                """
                session["user"] = create_user_session(existing_user)
                flash("Login Successful", "success")

                """
                Redirects to the URL in the next_url variable or to the home
                page if next_url contains no value.
                """
                return redirect(next_url or url_for('index'))

            else:
                """
                Invalid email address inputted by user. Code for message
                categories is from https://flask.palletsprojects.com/en/1.1.x/
                patterns/flashing/. Code for redirecting to the previous page
                is from https:// stackoverflow.com/questions/39777171/
                how-to-get-the-previous-url-in-flask/39777426.
                """
                flash("Incorrect Email Address and/or Password", "error")
                return redirect(request.referrer)

        else:
            """
            Invalid password inputted by user. Code for message categories is
            from https:// flask.palletsprojects.com/en/1.1.x/patterns/flashing/
            and code for redirecting to the previous page is from https://
            stackoverflow.com/questions/39777171/
            how-to-get-the-previous-url-in-flask/39777426.
            """
            flash("Incorrect Email Address and/or Password", "error")
            return redirect(url_for("sign_in"))

    return render_template("sign_in.html", page_title="Sign In")


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    """
    A view to return the sign up page, and if the request method is post,
    verify that the email address inputted is not already registered and add
    the user's details to the users database. Adds the user's email address to
    the newsletters database if they opt to sign up to the newsletter and signs
    the user in.
    """
    if request.method == "POST":
        """
        Gets the next search perameter from the URL. Code is from https://
        blog.tecladocode.com/handling-the-next-url-when-logging-in-with-flask/
        """
        next_url = request.form.get('next')

        # Checks if the email entered already exists in the database.
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            """
            User's email address is already registered. Code for message
            categories is from https://flask.palletsprojects.com/en/1.1.x/
            patterns/flashing/. Code for redirecting to the previous page is
            from https://stackoverflow.com/questions/39777171/
            how-to-get-the-previous-url-in-flask/39777426.
            """
            flash("Email already registered", "error")
            return redirect(request.referrer)

        else:
            # Adds the user's details to the database.
            sign_up = {
                "first_name": request.form.get("first_name"),
                "last_name": request.form.get("last_name"),
                "email": request.form.get("email"),
                "password": generate_password_hash(
                    request.form.get("password")),
                "user_type": "standard"
            }
            mongo.db.users.insert_one(sign_up)

            # Puts the user's details in the session cookie
            session["user"] = create_user_session(sign_up)

        if request.form.get("newsletter_signup") == "on":
            """
            Adds the user's email address to the newsletter database if the
            user toggled the newsletter sign up switch to on.
            """
            mongo.db.newsletter.insert_one(
                {"email": request.form.get("email")})

        """
        Code for message categories is from https://flask.palletsprojects.com/
        en/1.1.x/patterns/flashing/
        """
        flash("Sign Up Successful!", "success")

        if next_url:
            return redirect(next_url)

        else:
            return redirect(url_for('index'))

    return render_template("sign_up.html", page_title="Sign Up")


@app.route("/account")
@login_required
def account():
    """Gets the user's reviews and returns the user's account page."""

    user = "{} {}".format(
        session['user']['first_name'], session['user']['last_name'])
    reviews = list(mongo.db.reviews.find({"reviewed_by": user}))

    """
    Code for pagination is from https://gist.github.com/mozillazg/
    69fb40067ae6d80386e10e105e6803c9
    """

    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=10)
    pagination_reviews = paginate_items(reviews, offset, per_page)
    pagination = paginate(reviews, page, per_page)

    return render_template(
        "account.html",
        page_title="Account",
        reviews=pagination_reviews,
        pagination=pagination)


@app.route("/product_management")
@login_required
@admin_required
def product_management():
    """A view to return all the products and sort and paginates them. Code for
    the sort search perameter is from https://www.kite.com/python/answers/
    how-to-get-parameters-from-a-url-using-flask-in-python
    """
    sort_by = request.args.get("sort")

    """
    Code for the sort method is from https://docs.mongodb.com/manual/reference/
    method/cursor.sort/index.html
    """
    if sort_by:
        products = list(mongo.db.products.find().sort(sort_items(sort_by)))

    else:
        products = list(mongo.db.products.find().sort('name', 1))

    """
    Pagination code is from https://gist.github.com/mozillazg/
    69fb40067ae6d80386e10e105e6803c9
    """
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=10)
    pagination_products = paginate_items(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    return render_template(
        "product_management.html",
        page_title="Product Management",
        products=pagination_products,
        pagination=pagination)


@app.route("/sign_out")
def sign_out():
    """
    Signs the user out and returns the user to the previous page or the home
    page. Code for message categories is from https://flask.palletsprojects.com
    /en/1.1.x/patterns/flashing/ and code for next search perameter is from
    https://blog.tecladocode.com/
    handling-the-next-url-when-logging-in-with-flask/
    """
    next_url = request.form.get('next')
    session.pop("user")
    flash("Sign Out Successful", "success")
    return redirect(next_url or url_for('index'))


@app.route("/add_review/<product_id>", methods=["GET", "POST"])
@login_required
def add_review(product_id):
    """
    A view to return the add review page, and if the request method is post,
    adds the data inputted to the database and updates the product's ratings.
    """
    if request.method == 'POST':
        """
        Gets the next search perameter from the URL. Code is from https://
        blog.tecladocode.com/handling-the-next-url-when-logging-in-with-flask/
        """
        next_url = request.form.get('next')

        # Gets the product's ratings from the database
        product_ratings = mongo.db.products.find_one(
            {"_id": ObjectId(product_id)}, product_ratings_query())

        """
        Counts the number of reviews in the database for the product.
        Code is from https://docs.mongodb.com/manual/reference/method/
        db.collection.count/
        """
        product_count = mongo.db.reviews.count(
            {"product": product_ratings['name']})

        """
        Adds the details entered into the form to a dictionary. Code for date
        added is from https://www.w3schools.com/python/python_datetime.asp
        """
        review = {
            "overall_rating": int(request.form.get('overall_rating')),
            "performance_rating": int(request.form.get('performance_rating')),
            "usability_rating": int(request.form.get('usability_rating')),
            "price_rating": int(request.form.get('price_rating')),
            "quality_rating": int(request.form.get('quality_rating')),
            "review_title": request.form.get('review_title'),
            "review": request.form.get('review'),
            "product": product_ratings['name'],
            "date_added": datetime.datetime.now(),
            "reviewed_by": "{} {}".format(session['user']['first_name'],
                                          session['user']['last_name'])
        }

        # Calculates the product's new ratings
        new_ratings = add_ratings(product_ratings, product_count, review)

        """
        Updates the product's feature ratings in the products database.
        Code is from https://docs.mongodb.com/manual/reference/method/
        db.collection.updateOne/
        """
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)}, {"$set": new_ratings})

        # Updates the product's star ratings in the database.
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)},
            star_rating(new_rating=int(request.form.get('overall_rating'))))

        # Adds the review to the database
        mongo.db.reviews.insert_one(review)

        return redirect(next_url)

    else:
        """
        Aborts the request and returns a status code of 400 if the URL does not
        contain a next search perameter. Code is from https://
        flask.palletsprojects.com/en/1.1.x/api/#flask.abort
        """
        if request.args.get('next') is None:
            abort(400)

        # Gets the product's details from the products databse
        product = mongo.db.products.find_one({'_id': ObjectId(product_id)})

        """
        Aborts the request and returns a status of 404 if the product does not
        exist. Code is from https://flask.palletsprojects.com/en/1.1.x/api/
        #flask.abort
        """
        if product is None:
            abort(404)

        return render_template("add_review.html", page_title="Add Review",
                               product_id=product_id)


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    """
    A view to return the edit review page, and if the request method is post,
    updates the review in the database and updates the product's ratings.
    """
    if request.method == 'POST':
        """
        Gets the next search perameter from the URL. Code is from https://
        blog.tecladocode.com/handling-the-next-url-when-logging-in-with-flask/
        """
        next_url = request.form.get('next')

        # Gets the review's ratings from the database
        user_ratings = mongo.db.reviews.find_one(
            {'_id': ObjectId(review_id)}, user_ratings_query())

        # Gets the product's ratings from the database
        product_ratings = mongo.db.products.find_one(
            {"name": user_ratings['product']}, product_ratings_query())

        """
        Counts the number of reviews in the database for the product.
        Code is from https://docs.mongodb.com/manual/reference/method/
        db.collection.count/
        """
        product_count = mongo.db.reviews.count(
            {"product": user_ratings['product']})

        """
        Adds the details entered into the form to a dictionary. Code for date
        added is from https://www.w3schools.com/python/python_datetime.asp
        """
        review = {
            "overall_rating": int(request.form.get('overall_rating')),
            "performance_rating": int(request.form.get('performance_rating')),
            "usability_rating": int(request.form.get('usability_rating')),
            "price_rating": int(request.form.get('price_rating')),
            "quality_rating": int(request.form.get('quality_rating')),
            "review_title": request.form.get('review_title'),
            "review": request.form.get('review'),
            "date_added": datetime.datetime.now(),
        }

        # Calculates the product's new ratings
        new_ratings = edit_ratings(
            user_ratings, product_ratings, product_count, review)

        """
        Updates the product's feature ratings in the database. Code is
        from https://docs.mongodb.com/manual/reference/method/
        db.collection.updateOne/
        """
        mongo.db.products.update_one(
            {'_id': product_ratings['_id']}, {"$set": new_ratings})

        """
        Updates the product's feature ratings in the database if the user has
        changed the overall rating value in the form.
        """
        if (int(request.form.get('overall_rating')) != user_ratings
                ['overall_rating']):

            mongo.db.products.update_one({"_id": review_id}, star_rating(
                request.form.get('overall_rating'), user_ratings
                ['overall_review']))

        """
        Updates the review in the database. Code is from https://
        docs.mongodb.com/manual/reference/method/db.collection.updateOne/
        """
        mongo.db.reviews.update_one(
            {'_id': ObjectId(review_id)}, {"$set": review})

        return redirect(next_url)

    else:
        """
        Aborts the request and returns a status code of 400 if the URL does not
        contain a next search perameter. Code is from https://
        flask.palletsprojects.com/en/1.1.x/api/#flask.abort
        """
        if request.args.get('next') is None:
            abort(400)

        """
        Gets the review author's details from the database. Code for
        returning selected fields from https://docs.mongodb.com/manual/tutorial
        /project-fields-from-query-results/
        """
        review = mongo.db.reviews.find_one(
            {"_id": ObjectId(review_id)}, {"reviewed_by": 1, "_id": 0})

        """
        Aborts the request and returns a status of 404 if no review is found or
        a 403 status if the review author is not the user currently signed in.
        Code is from https://flask.palletsprojects.com/en/1.1.x/api/
        #flask.abort
        """
        if review is None:
            return abort(404)

        elif "{} {}".format(session['user']['first_name'], session['user']
                            ['last_name']) != review['reviewed_by']:
            return abort(403)

        else:
            # Gets the review from the database
            review = mongo.db.reviews.find_one({'_id': ObjectId(review_id)})

            return render_template('edit_review.html',
                                   page_title='Edit Review', review=review)


@app.route("/delete_review/<review_id>")
@login_required
def delete_review(review_id):
    """
    A view to delete the review from the database and updates the product's
    ratings.
    """

    """
    Gets the next URL search perameter and aborts the request and returns a
    status code of 400 if the URL does not contain a next search perameter.
    Code is from https://blog.tecladocode.com/
    handling-the-next-url-when-logging-in-with-flask/ and https://
    flask.palletsprojects.com/en/1.1.x/api/#flask.abort
    """

    next_url = request.args.get('next')

    if next_url is None:
        abort(400)

    """
    Gets the review author's details from the database. Code for
    returning selected fields from https://docs.mongodb.com/manual/tutorial/
    project-fields-from-query-results/
    """
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)}, {
        "reviewed_by": 1, "_id": 0})

    """
    Aborts the request and returns a 404 status if no review is returned and a
    403 status if the review author is not the user currently signed in.
    Code is from https://flask.palletsprojects.com/en/1.1.x/api/#flask.abort
    """

    if review is None:
        return abort(404)

    elif "{} {}".format(session['user']['first_name'], session['user']
                        ['last_name']) != review['reviewed_by']:
        return abort(403)

    else:
        # Gets the review's ratings from the database
        user_ratings = mongo.db.reviews.find_one(
            {'_id': ObjectId(review_id)}, user_ratings_query())

        # Gets the product's ratings from the database
        product_ratings = mongo.db.products.find_one(
            {"name": user_ratings['product']}, product_ratings_query())

        """
        Counts the number of reviews in the database for the product.
        Code is from https://docs.mongodb.com/manual/reference/method/
        db.collection.count/
        """
        product_count = mongo.db.reviews.count_documents(
            {"product": user_ratings['product']})

        # Calculates the product's new ratings
        new_ratings = delete_ratings(
            user_ratings, product_ratings, product_count)

        """
        Updates the product's feature ratings in the products database.
        Code is from https://docs.mongodb.com/manual/reference/method/
        db.collection.updateOne/
        """
        mongo.db.products.update_one(
            {'_id': product_ratings['_id']}, {"$set": new_ratings})

        # Updates the product's star ratings in the products database
        mongo.db.products.update_one({"name": user_ratings['product']},
                                     star_rating(
            prev_rating=user_ratings['overall_rating']))

        # Deletes the review from the reviews database
        mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})

        """
        Code for message categories is from https://flask.palletsprojects.com/
        en/1.1.x/patterns/flashing/
        """
        flash("Review Successfully Deleted", "Success")

        return redirect(next_url)


@app.route("/add_product", methods=["GET", "POST"])
@login_required
@admin_required
def add_product():
    if request.method == "POST":
        """
        A view to add the product to the database and update the relevant
        category's brands list.
        """

        """
        Gets the details entered into the form and convert them into a
        dictionary.
        """
        product = request.form.to_dict()

        """
        Converts the price to the decimal 128 data type. Code is from https://
        pymongo.readthedocs.io/en/stable/api/bson/decimal128.html
        """
        product['price'] = Decimal128(product['price'])

        """
        Generates a list of all the keys in the products dictionary. Code is
        from https://stackoverflow.com/questions/6307394/
        removing-dictionary-entries-with-no-values-python
        """
        keys = list(product.keys())

        """
        Deletes any products from the dictionary which have a value of an empty
        string.
        """
        for key in keys:
            if product[key] == "":
                del product[key]

        # Adds the product details to the database
        mongo.db.products.insert_one(product)

        """
        Adds the brand to the relevant brands list in the database.
        Code is from https://docs.mongodb.com/manual/reference/operator/update/
        addToSet/
        """
        mongo.db.categories.update_one({"name": product['category']}, {
                                       "$addToSet": {"brands": product['brand']
                                                     }})

        return redirect(url_for('product_management'))

    # Get a list of categories from the database
    categories = mongo.db.categories.find()

    return render_template('add_product.html', page_title='Add Product',
                           categories=categories)


@app.route("/edit_product/<product_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    """
    A view to update the product in the database and update the relevant
    category's brands list.
    """
    if request.method == "POST":
        """
        Gets the details entered into the form and convert them into a
        dictionary.
        """
        product = request.form.to_dict()

        """
        Converts the price to the decimal 128 data type. Code is from https://
        pymongo.readthedocs.io/en/stable/api/bson/decimal128.html
        """
        product['price'] = Decimal128(product['price'])

        """
        Generates a list of all the keys in the products dictionary. Code is
        from https://stackoverflow.com/questions/6307394/
        removing-dictionary-entries-with-no-values-python
        """
        keys = list(product.keys())

        """
        Deletes any products from the dictionary which have a value of an empty
        string.
        """
        for key in keys:
            if product[key] == "":
                del product[key]

        """
        Adds the product details to the products database Code is from https://
        docs.mongodb.com/manual/reference/method/db.collection.updateOne/
        """
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)}, {"$set": product})

        """
        Adds the brand to the relevant brands list in the categories database.
        Code is from https://docs.mongodb.com/manual/reference/operator/update/
        addToSet/
        """
        mongo.db.categories.update_one({"name": product['category']}, {
                                       "$addToSet": {"brands": product['brand']
                                                     }})

        return redirect(url_for('product_management'))

    # Gets the product's details from the databse
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})

    """
    Aborts the request and returns a 404 status if the product does not
    exist. Code is from https://flask.palletsprojects.com/en/1.1.x/api/
    #flask.abort
    """
    if product is None:
        abort(404)

    # Gets a list of categories from the database
    categories = mongo.db.categories.find()

    return render_template(
        'edit_product.html',
        page_title='Edit Product',
        categories=categories,
        product=product
    )


@app.route("/delete_product/<product_id>")
@login_required
@admin_required
def delete_product(product_id):
    """
    A view to delete the product from the database and update the relevant
    category's brands list.
    """

    """
    Gets the product's name and category from the database. Code for returning
    selected fields is from https://docs.mongodb.com/manual/tutorial
    project-fields-from-query-results/
    """
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)},
                                         {"brand": 1, "category": 1, "_id": 0})

    """
    Counts the number of products in the database which are from product's
    category and brand. Code is from https://docs.mongodb.com/manual/reference/
    method/db.collection.count/ and https://docs.mongodb.com/manual/tutorial/
    project-fields-from-query-results/
    """
    brand_count = mongo.db.products.count(
        {"brand": product['brand'], "category": product['category']})

    """
    Deletes the brand from the relevant category's brands array in the database
    if the brand count is one. Code is from https://docs.mongodb.com/manual/
    reference/operator/update/pull/
    """
    if brand_count == 1:
        mongo.db.categories.update_one({"name": product['category']}, {
                                       "$pull": {"brands": product['brand']}})

    # Deletes the product
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})

    """
    Code for message categories is from https://flask.palletsprojects.com/
    en/1.1.x/patterns/flashing/
    """
    flash("Product Successfully Deleted", "Success")

    return redirect(url_for('product_management'))


@app.errorhandler(400)
def bad_request(e):
    """
    Redirects to the home page if the HTTP request returns a status of 400.
    Code is from https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages
    """
    return redirect(url_for('index'))


@app.errorhandler(403)
def page_forbidden(e):
    """
    Returns the 403 page if the HTTP request returns a status of 403.
    Code is from https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages
    """
    return render_template("403.html", page_title=403)


@app.errorhandler(404)
def page_not_found(e):
    """
    Returns the 404 page if the HTTP request returns a status of 404.
    Code is from https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages
    """
    return render_template("404.html", page_title=404)


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)
