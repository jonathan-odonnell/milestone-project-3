import os
from functools import wraps
from flask import (Flask, flash, jsonify, render_template,
                   redirect, request, session, url_for, abort)
from flask_pymongo import PyMongo
from flask_paginate import get_page_args
from bson.objectid import ObjectId
from bson.decimal128 import Decimal128
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from utils import (add_ratings, create_user_session, delete_ratings,
                   edit_ratings, paginate, paginate_products,
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
    Prevents users who are not signed in from accessing the page and redirects
    them to the sign in page. Code is from https://flask.palletsprojects.com/
    en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            """
            Code for message categories is from https://
            flask.palletsprojects.com/en/1.1.x/patterns/flashing/
            """
            flash("Please sign in to view this page", "error")
            return redirect(url_for('sign_in'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Prevents users who are not admins from accessing the page and
    redirects them to the 403 page. Code is from https://
    flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/ and
    https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session['user']['user_type'] != "admin":
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
@app.route("/index")
def index():
    """
    Retuns the index.html template
    """
    return render_template("index.html", page_title="Home")


@app.route("/newsletter", methods=["POST"])
def newsletter():
    """
    Adds the email to the newsletters database and returns a success status.
    Code for the success status is from https://stackoverflow.com/questions/
    26079754/ flask-how-to-return-a-success-status-code-for-ajax-call/
    26080784#26080784
    """
    mongo.db.newsletter.insert_one(
        {"email": request.form.get("email")})
    return jsonify(success=True)


@app.route('/reviews')
@app.route("/reviews/<category>")
def reviews(category="all"):
    """
    Gets the search parameters from the url, converts them to a dictionary and
    generates the search query.
    """
    search_params = request.args.to_dict()
    search_params['category'] = category
    query = search(search_params)

    # Set the page title
    page_title = category

    # Updates the page title if the category is equal to all
    if category == "All":
        page_title = "Reviews"

    """
    Gets a list of all the products that satisfy the search criteria.
    Code for the sort method is from https://docs.mongodb.com/manual/reference/
    method/cursor.sort/index.html
    """
    products = list(mongo.db.products.find(query).sort(
        sort_items(request.args.get("sort"))))

    # Count the number of products in the products list
    total = len(products)

    """
    Paginate products with 6 products to a page.
    Code is from https://gist.github.com/mozillazg/
    69fb40067ae6d80386e10e105e6803c9
    """
    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=6)
    pagination_products = paginate_products(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    """
    Generate pagination info. Code is adapted from
    https://pythonhosted.org/Flask-paginate/
    """
    record_numbers = pagination.info[48:53]
    if category == "All":
        pagination_info = 'Displaying {} of {} reviews found for "{}"'.format(
            record_numbers, total, search_params['search'])
    else:
        pagination_info = 'Displaying {} of {} reviews'.format(
            record_numbers, total)

    # Renders the reviews.html template
    return render_template(
        "reviews.html",
        page_title=page_title,
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
    # Gets the product from the products database
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)})

    # Sets the page title
    page_title = product["name"] + " Review"

    # Sets the value of the current user

    current_user = None
    if "user" in session:
        current_user = "{} {}".format(session['user']['first_name'],
                                      session['user']['last_name'])

    # Gets the review from the reviews database
    reviews = list((mongo.db.reviews.find(
        {"product": product["name"]})))

    for review in reviews:
        """
        Updates the date_added value in the review dictionary to be in the
        correct format. Code is from https://www.w3schools.com/python/
        python_datetime.asp
        """
        review['date_added'] = review['date_added'].strftime("%d %B %Y")

    # Renders the review_details template
    return render_template("review_details.html",
                           page_title=page_title,
                           product=product,
                           reviews=reviews,
                           current_user=current_user)


@app.route("/up_vote", methods=["POST"])
def up_vote():
    """
    Increases the up vote, gets the updated value and returns a success
    status. Code for increment is from https://docs.mongodb.com/manual/
    reference/operator/update/inc/ and code for the success status is from
    https://stackoverflow.com/questions/26079754/
    flask-how-to-return-a-success-status-code-for-ajax-call/
    26080784#26080784
    """
    review_id = review_id = request.form.get('review_id')
    mongo.db.reviews.update_one(
        {'_id': ObjectId(review_id)}, {"$inc": {"up_vote": 1}})
    up_vote = mongo.db.reviews.find_one({"_id": ObjectId(review_id)},
                                        {"up_vote": 1, "_id": 0})

    return jsonify({"up_vote": up_vote['up_vote'], "success": True})


@app.route("/down_vote", methods=["POST"])
def down_vote():
    """
    Increases the down vote, gets the updated value and returns a success
    status. Code for increment is from https://docs.mongodb.com/manual/
    reference/operator/update/inc/ and code for the success status is from
    https://stackoverflow.com/questions/26079754/
    flask-how-to-return-a-success-status-code-for-ajax-call/
    26080784#26080784
    """
    review_id = request.form.get('review_id')
    mongo.db.reviews.update_one(
        {'_id': ObjectId(review_id)}, {"$inc": {"down_vote": 1}})
    down_vote = mongo.db.reviews.find_one({"_id": ObjectId(review_id)},
                                          {"down_vote": 1, "_id": 0})

    return jsonify({"down_vote": down_vote['down_vote'], "success": True})


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        """
        Adds the data entered in the contact form to the contact database
        if the request method is post and returns a success status.
        Code for the success status is from https://stackoverflow.com/questions
        /26079754/flask-how-to-return-a-success-status-code-for-ajax-call/
        26080784#26080784
        """
        mongo.db.contact.insert_one(request.form.to_dict())
        return jsonify(success=True)

    # If the request method is not post, return the contact.html template.
    return render_template("contact.html", page_title="Contact Us")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        # Check if the email entered already exists in the database.
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            if check_password_hash(existing_user["password"],
                                   request.form.get("password")):
                """
                If the user exists, check the hashed password matches the
                password entered by the user and add the user's details to the
                session cookie. Add a message informing the user that the sign
                in was successful and return them to the previous page. Code
                for message categories is from https://
                flask.palletsprojects.com/en/1.1.x/patterns/flashing/
                """
                session["user"] = create_user_session(existing_user)
                flash("Login Successful", "success")
                return redirect(request.form.get("next"))

            else:
                """
                If the user does not exist, add a message informing them that
                their username and/or password is incorrect. Code for message
                categories is from https://flask.palletsprojects.com/en/1.1.x/
                patterns/flashing/
                """
                flash("Incorrect Email Address and/or Password", "error")
                return redirect(url_for("sign_in"))

        else:
            """
            If the passwords do not match, return the user to the sign in page
            and add a message informing them that their username and/or
            password is incorrect. Code for message categories is from https://
            flask.palletsprojects.com/en/1.1.x/patterns/flashing/
            """
            flash("Incorrect Email Address and/or Password", "error")
            return redirect(url_for("sign_in"))

    # Render the sign in page template.
    return render_template("sign_in.html", page_title="Sign In")


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        # Check if the email entered already exists in the database.
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            """
            If the user exist, return the user to the sign up page
            and add a message informing them that the email is already
            registered. Code for message categories is from https://
            flask.palletsprojects.com/en/1.1.x/patterns/flashing/
            """
            flash("Email already registered", "error")
            return redirect(url_for("sign_up"))

        else:
            """
            If the user does not already exist, add their details to the users
            database.
            """
            sign_up = {
                "first_name": request.form.get("first_name").lower(),
                "last_name": request.form.get("last_name").lower(),
                "email": request.form.get("email").lower(),
                "password": generate_password_hash(
                    request.form.get("password")),
                "user_type": "standard"
            }
            mongo.db.users.insert_one(sign_up)

            # Put the user's details in the session cookie
            session["user"] = create_user_session(sign_up)

        if request.form.get("newsletter_signup") == "on":
            """
            If the user toggled the newsletter sign up switch to on, add the
            user's email address to the newsletter database.
            """
            mongo.db.newsletter.insert_one(
                {"email": request.form.get("email")})

        """
        Add a message informing the user that the sign up was successful and
        return them to the previous page. Code for message categories is from
        https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
        """
        flash("Registration Successful!", "success")
        return redirect(request.form.get("next"))

    # Render the sign_up.html template
    return render_template("sign_up.html", page_title="Sign Up")


@app.route("/product_management", methods=["GET", "POST"])
@login_required
@admin_required
def product_management():
    """
    Get the sort_by argument from the query string. Code is from https://
    www.kite.com/python/answers/
    how-to-get-parameters-from-a-url-using-flask-in-python
    """
    sort_by = request.args.get("sort")

    if sort_by:
        """
        If sort_by has a value, get all the products from the database and sort
        them according to the value of the sort_by variable. Code for the sort
        method is from https://docs.mongodb.com/manual/reference/method/
        cursor.sort/index.html
        """
        products = list(mongo.db.products.find().sort(sort_items(sort_by)))

    else:
        """
        Get all the products from the database and sort them by name in
        asscending order.
        """
        products = list(mongo.db.products.find().sort('name', 1))

    """
    Paginate products with 10 to a page.
    Code is from https://gist.github.com/mozillazg/
    69fb40067ae6d80386e10e105e6803c9
    """

    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=10)
    pagination_products = paginate_products(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    # Render the product_management.html template.

    return render_template(
        "product_management.html",
        page_title="Product Management",
        products=pagination_products,
        pagination=pagination)


@app.route("/logout")
def logout():
    """
    Remove the session cookie containing the user's details, add a message
    informing the user that they have been successfully signed out and return
    them to the sign in page. Code for message categories is from https://
    flask.palletsprojects.com/en/1.1.x/patterns/flashing/
    """
    session.pop("user")
    flash("Logout Successful", "success")
    return redirect(url_for('sign_in'))


@app.route("/reviews/add_review/", methods=["GET", "POST"])
@login_required
def add_review():
    if request.method == 'POST':
        # Gets the product's ratings from the product database
        product_ratings = mongo.db.products.find_one(
            {"name": request.form.get('product')}, product_ratings_query())

        """
        Counts the number of reviews in the reviews database for the product.
        Code is from https://docs.mongodb.com/manual/reference/method/
        db.collection.count/
        """
        product_count = mongo.db.reviews.count(
            {"product": request.form.get('product')})

        """
        Get the details entered into the form and convert them into a
        dictionary.
        """
        review = request.form.to_dict()

        # Calculates the product's new ratings
        new_ratings = add_ratings(product_ratings, product_count, request)

        """
        Updates the product's feature ratings in the products database.
        Code is from https://docs.mongodb.com/manual/reference/method/
        db.collection.updateOne/
        """
        mongo.db.products.update_one(
            {'name': request.form.get('product')}, {"$set": new_ratings})

        # Updates the product's star ratings in the products database.
        mongo.db.products.update_one(
            {'name': request.form.get('product')},
            star_rating(new_rating=int(request.form.get('overall_rating'))))

        """
        Adds the date_added and created_by to the
        review dictionary. Date code is from
        https://www.w3schools.com/python/python_datetime.asp
        """
        review['date_added'] = datetime.datetime.now()
        review['created_by'] = session['user']['first_name'] + \
            " " + session['user']['last_name']

        # Adds the review to the reviews database
        mongo.db.reviews.insert_one(review)

        # Returns the user to the previous page
        return redirect(request.form.get('next'))

    # Renders the add_review.html template
    return render_template("add_review.html", page_title="Add Review")


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    if request.method == 'POST':
        # Gets the review's ratings from the reviews database
        user_ratings = mongo.db.reviews.find_one(
            {'_id': ObjectId(review_id)}, user_ratings_query())

        # Gets the product's ratings from the product database
        product_ratings = mongo.db.products.find_one(
            {"name": user_ratings['product']}, product_ratings_query())

        """
        Counts the number of reviews in the reviews database for the product.
        Code is from https://docs.mongodb.com/manual/reference/method/
        db.collection.count/
        """
        product_count = mongo.db.reviews.count(
            {"product": user_ratings['product']})

        """
        Get the details entered into the form and convert them into a
        dictionary.
        """
        review = request.form.to_dict()

        # Calculates the product's new ratings
        new_ratings = edit_ratings(
            user_ratings, product_ratings, product_count, review)

        # Updates the product's feature ratings in the products database
        mongo.db.products.update_one(
            {'name': request.form.get('product')}, {"$set": new_ratings})

        if (int(request.form.get('overall_rating')) != user_ratings
                ['overall_rating']):
            """
            Updates the product's feature ratings in the products database,
            if the user has changed the overall rating value in the form.
            """
            mongo.db.products.update_one({"_id": review_id}, star_rating(
                request.form.get('overall_rating'), user_ratings
                ['overall_review']))

        """
        Adds date_added value to the review dictionary.
        Code is from https://www.w3schools.com/python/python_datetime.asp
        """
        review['date_added'] = datetime.datetime.now()

        """
        Updates the review in the reviews database. Code is from https://
        docs.mongodb.com/manual/reference/method/db.collection.updateOne/
        """
        mongo.db.reviews.update_one(
            {'_id': ObjectId(review_id)}, {"$set": review})

        # Returns the user to the previous page
        return redirect(request.form.get('next'))

    # Gets the review author's details from the reviews database
    user = mongo.db.reviews.find_one(
        {"_id": ObjectId(review_id)}, {"created_by": 1, "_id": 0})

    if user is None:
        """
        Returns the user to the 404 page if no user is returned. Code is
        from https://flask.palletsprojects.com/en/1.1.x/patterns
        /errorpages/
        """
        return abort(404)

    elif "{} {}".format(session['user']['first_name'], session['user']
                        ['last_name']) != user['created_by']:
        """
        Returns the user to the 403 page is the user is not the
        author of the review. Code is from https://
        flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
        """
        return abort(403)

    else:
        # Gets the review from the reviews database
        review = mongo.db.reviews.find_one({'_id': ObjectId(review_id)})

        # Renders the edit_review.html template
        return render_template('edit_review.html',
                               page_title='Edit Review', review=review)


@app.route("/delete_review/<review_id>", methods=["GET", "POST"])
@login_required
def delete_review(review_id):
    # Gets the review author's details from the reviews database
    user = mongo.db.reviews.find_one({"_id": ObjectId(review_id)}, {
                                     "created_by": 1, "_id": 0})

    if user is None:
        """
        Returns the user to the 404 page if no user is returned.
        Code is from https://flask.palletsprojects.com/en/1.1.x/
        patterns/errorpages/
        """
        return abort(404)

    elif "{} {}".format(session['user']['first_name'], session['user']
                        ['last_name']) != user['created_by']:
        """
        Returns the user to the 403 page is the user is not the
        author of the review. Code is from https://flask.palletsprojects.com/
        en/1.1.x/patterns/errorpages/
        """
        return abort(403)

    else:
        # Gets the review's ratings from the reviews database
        user_ratings = mongo.db.reviews.find_one(
            {'_id': ObjectId(review_id)}, user_ratings_query())

        # Gets the product's ratings from the product database
        product_ratings = mongo.db.products.find_one(
            {"name": user_ratings['product']}, product_ratings_query())

        """
        Counts the number of reviews in the reviews database for the product.
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
            {'name': request.form.get('product')}, {"$set": new_ratings})

        # Updates the product's star ratings in the products database
        mongo.db.products.update_one({"name": user_ratings['product']},
                                     star_rating(
            prev_rating=user_ratings['overall_rating']))

        # Deletes the review from the reviews database
        mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})

        """
        Returns the user to the previous page. Code is from https://
        stackoverflow.com/questions/39777171/
        how-to-get-the-previous-url-in-flask/39777426
        """
        return redirect(request.referrer)


@app.route("/add_product", methods=["GET", "POST"])
@login_required
@admin_required
def add_product():
    if request.method == "POST":
        """
        Get the details entered into the form and convert them into a
        dictionary.
        """
        product = request.form.to_dict()

        """
        Generate a list of all the keys in the products dictionary. Code is
        from https://stackoverflow.com/questions/6307394/
        removing-dictionary-entries-with-no-values-python
        """
        keys = list(product.keys())

        """
        Delete any products from the dictionary which have a value of an empty
        string.
        """
        for key in keys:
            if product[key] == "":
                del product[key]

        """
        Converts the price to the decimal 128 data type. Code is from https://
        pymongo.readthedocs.io/en/stable/api/bson/decimal128.html
        """
        product['price'] = Decimal128(product['price'])

        # Add the product details to the products database
        mongo.db.products.insert_one(product)

        # Return the user to the product management page
        return redirect(url_for('product_management'))

    # Render the add_product.html template
    return render_template('add_product.html', page_title='Add Product')


@app.route("/edit_product/<product_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    if request.method == "POST":
        """
        Get the details entered into the form and convert them into a
        dictionary.
        """
        product = request.form.to_dict()

        """
        Generate a list of all the keys in the products dictionary. Code is
        from https://stackoverflow.com/questions/6307394/
        removing-dictionary-entries-with-no-values-python
        """
        keys = list(product.keys())

        """
        Delete any products from the dictionary which have a value of an empty
        string.
        """
        for key in keys:
            if product[key] == "":
                del product[key]

        """
        Converts the price to the decimal 128 data type. Code is from https://
        pymongo.readthedocs.io/en/stable/api/bson/decimal128.html
        """
        product['price'] = Decimal128(product['price'])

        """
        Add the product details to the products database
        Code is from https://docs.mongodb.com/manual/reference/
        method/db.collection.updateOne/
        """
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)}, {"$set": product})

        # Return the user to the product management page
        return redirect(url_for('product_management'))

    # Get the product's details from the products databse
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})

    if product is None:
        """
        If the product does not extis return the user to the 404 page. Code is
        from https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
        """
        abort(404)

    # Get a list of categories from the categories database
    categories = mongo.db.categories.find()

    # Render the edit_product.html template
    return render_template(
        'edit_product.html',
        page_title='Edit Product',
        categories=categories,
        product=product
    )


@app.route("/delete_product/<product_id>", methods=["GET", "POST"])
@login_required
@admin_required
def delete_product(product_id):
    # Deletes the product
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    return redirect(url_for('product_management'))


@app.errorhandler(403)
def page_forbidden(e):
    """
    Renders the 403.html template if the HTTP request returns a 403
    page not found error is returned. Code is from
    https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
    """
    return render_template("403.html", page_title=403)


@app.errorhandler(404)
def page_not_found(e):
    """
    Renders the 404.html template if the HTTP request returns a 404
    page not found error is returned. Code is from
    https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
    """
    return render_template("404.html", page_title=404)


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)
