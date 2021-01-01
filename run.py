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
    Prevents users who are not signed in from accessing the page and redirects
    to the sign in page. Code is from https://flask.palletsprojects.com/
    en/1.1.x/patterns/viewdecorators/ and https://blog.tecladocode.com/
    handling-the-next-url-when-logging-in-with-flask/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            """
            Code for message categories is from https://
            flask.palletsprojects.com/en/1.1.x/patterns/flashing/
            """
            flash("Please sign in to view this page", "error")
            return redirect(url_for('sign_in', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Prevents users who are not admins from accessing the page and returns a
    status of 403. Code is from https://flask.palletsprojects.com/en/1.1.x/
    patterns/viewdecorators/ and https://flask.palletsprojects.com/en/1.1.x/
    patterns/errorpages/
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
    Renders the index.html template
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
def reviews(category="All"):
    """
    Gets the search parameters from the URL, converts them to a dictionary,
    adds the category if the category is not equal to all and generates the
    search query. Code for search perameters is from
    https://www.kite.com/python/answers/
    how-to-get-parameters-from-a-url-using-flask-in-python
    """
    search_params = request.args.to_dict()

    if category != "All":
        search_params['categories'] = category

    query = search(search_params, category)

    # Sets the page title
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

    """
    Gets the relevent filters from the categories database. Code for returning
    selected fields from https://docs.mongodb.com/manual/tutorial/
    project-fields-from-query-results/
    """
    if category == "All":
        filters = list(mongo.db.categories.find({}, {"name": 1, "_id": 0}))

    else:
        filters = mongo.db.categories.find_one(
            {"name": category}, {"brands": 1, "prices": 1, "_id": 0})

    # Counts the number of products in the products list.
    total = len(products)

    """
    Paginates products with 6 products to a page.
    Code is from https://gist.github.com/mozillazg/
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

    # Renders the reviews.html template
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
    Increases the up vote value by one. Code is from https://docs.mongodb.com
    /manual/reference/operator/update/inc/
    """
    review_id = review_id = request.form.get('review_id')
    mongo.db.reviews.update_one(
        {'_id': ObjectId(review_id)}, {"$inc": {"up_vote": 1}})

    """
    Gets the new up vote value from the reviews database. Code is from
    https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/
    """
    up_vote = mongo.db.reviews.find_one({"_id": ObjectId(review_id)},
                                        {"up_vote": 1, "_id": 0})

    """
    Returns a success status. Code is from https://stackoverflow.com/questions/
    26079754/flask-how-to-return-a-success-status-code-for-ajax-call/
    26080784#26080784
    """
    return jsonify({"up_vote": up_vote['up_vote'], "success": True})


@app.route("/down_vote", methods=["POST"])
def down_vote():
    """
    Increases the down vote value by one. Code is from https://docs.mongodb.com
    /manual/reference/operator/update/inc/
    """
    review_id = request.form.get('review_id')
    mongo.db.reviews.update_one(
        {'_id': ObjectId(review_id)}, {"$inc": {"down_vote": 1}})

    """
    Gets the new down vote value from the reviews database. Code is from
    https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/
    """
    down_vote = mongo.db.reviews.find_one({"_id": ObjectId(review_id)},
                                          {"down_vote": 1, "_id": 0})

    """
    Returns a success status. Code is from https://stackoverflow.com/questions/
    26079754/flask-how-to-return-a-success-status-code-for-ajax-call/
    26080784#26080784
    """
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

    # Renders the contact.html template.
    return render_template("contact.html", page_title="Contact Us")


@app.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        """
        Gets the next URL from the next field in the form.
        Code is from https://blog.tecladocode.com/
        handling-the-next-url-when-logging-in-with-flask/
        """
        next_url = request.form.get('next')

        # Checks if the email entered already exists in the database.
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            if check_password_hash(existing_user["password"],
                                   request.form.get("password")):
                """
                If the user exists, checks the hashed password matches the
                password entered by the user, add the user's details to the
                session cookie and adds a message informing the user that the
                sign in was successful. Code for message categories is from
                https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
                """
                session["user"] = create_user_session(existing_user)
                flash("Login Successful", "success")

                """
                Redirects to the URL in the next_url variable or to the home
                page if next_url contains no value.
                """
                if next_url:
                    return redirect(next_url)

                else:
                    return redirect(url_for('index'))

            else:
                """
                If the user does not exist, adds a message informing the user
                that their username and/or password is incorrect and redirects
                to the previous page. Code for message categories is from
                https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/.
                Code for redirecting to the previous page is from https://
                stackoverflow.com/questions/39777171/
                how-to-get-the-previous-url-in-flask/39777426.
                """
                flash("Incorrect Email Address and/or Password", "error")
                return redirect(request.referrer)

        else:
            """
            If the passwords do not match, adds a message informing the user
            that their username and/or password is incorrect and redirects
            to the sign in page. Code for message categories is from https://
            flask.palletsprojects.com/en/1.1.x/patterns/flashing/
            """
            flash("Incorrect Email Address and/or Password", "error")
            return redirect(url_for("sign_in"))

    # Renders the sign in page template.
    return render_template("sign_in.html", page_title="Sign In")


@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        """
        Gets the next URL from the next field in the form.
        Code is from https://blog.tecladocode.com/
        handling-the-next-url-when-logging-in-with-flask/
        """
        next_url = request.form.get('next')

        # Checks if the email entered already exists in the database.
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})

        if existing_user:
            """
            If the user exist, adds a message informing the user that the email
            is already registered and redirects to the previous page. Code
            for message categories is from https://flask.palletsprojects.com/
            en/1.1.x/patterns/flashing/. Code for redirecting to the previous
            page is from https://stackoverflow.com/questions/39777171/
            how-to-get-the-previous-url-in-flask/39777426.
            """
            flash("Email already registered", "error")
            return redirect(request.referrer)

        else:
            """
            Adds the user's details to the users database if they do not
            already exist.
            """
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
        Adds a message informing the user that the sign up was successful and
        redirects to the URL in the next_url variable or to the home page if
        next_url contains no value. Code for message categories is from
        https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
        """
        flash("Sign Up Successful!", "success")

        if next_url:
            return redirect(next_url)

        else:
            return redirect(url_for('index'))

    # Renders the sign_up.html template
    return render_template("sign_up.html", page_title="Sign Up")


@app.route("/account")
@login_required
def account():
    """
    Gets a list of the reviews the user has written from the reviews database.
    """
    user = "{} {}".format(
        session['user']['first_name'], session['user']['last_name'])
    reviews = list(mongo.db.reviews.find({"created_by": user}))

    """
    Paginates products with 10 to a page.
    Code is from https://gist.github.com/mozillazg/
    69fb40067ae6d80386e10e105e6803c9
    """

    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=10)
    pagination_reviews = paginate_items(reviews, offset, per_page)
    pagination = paginate(reviews, page, per_page)

    # Renders the account.html template.

    return render_template(
        "account.html",
        page_title="Account",
        reviews=pagination_reviews,
        pagination=pagination)


@app.route("/product_management", methods=["GET", "POST"])
@login_required
@admin_required
def product_management():
    """
    Gets the sort_by search perameter from the URL. Code is from
    https://www.kite.com/python/answers/
    how-to-get-parameters-from-a-url-using-flask-in-python
    """
    sort_by = request.args.get("sort")

    if sort_by:
        """
        If sort_by has a value, gets all the products from the database and
        sorts them according to the value of the sort_by variable. Code for the
        sort method is from https://docs.mongodb.com/manual/reference/method/
        cursor.sort/index.html
        """
        products = list(mongo.db.products.find().sort(sort_items(sort_by)))

    else:
        """
        Otherwise, gets all the products from the database and sort them by
        name in asscending order.
        """
        products = list(mongo.db.products.find().sort('name', 1))

    """
    Paginates products with 10 to a page.
    Code is from https://gist.github.com/mozillazg/
    69fb40067ae6d80386e10e105e6803c9
    """

    page, per_page, offset = get_page_args(
        page_parameter='page', per_page_parameter='per_page', per_page=10)
    pagination_products = paginate_items(products, offset, per_page)
    pagination = paginate(products, page, per_page)

    # Renders the product_management.html template.

    return render_template(
        "product_management.html",
        page_title="Product Management",
        products=pagination_products,
        pagination=pagination)


@app.route("/sign_out")
def sign_out():
    """
    Removes the session cookie containing the user's details, adds a message
    informing the user that they have been successfully signed out and
    redirects to the sign in page. Code for message categories is
    from https://flask.palletsprojects.com/en/1.1.x/patterns/flashing/
    """
    session.pop("user")
    flash("Sign Out Successful", "success")
    return redirect(url_for('sign_in'))


@app.route("/add_review/<product_id>", methods=["GET", "POST"])
@login_required
def add_review(product_id):
    if request.method == 'POST':
        # Gets the product's ratings from the product database
        product_ratings = mongo.db.products.find_one(
            {"_id": ObjectId(product_id)}, product_ratings_query())

        """
        Counts the number of reviews in the reviews database for the product.
        Code is from https://docs.mongodb.com/manual/reference/method/
        db.collection.count/
        """
        product_count = mongo.db.reviews.count(
            {"product": product_ratings['name']})

        """
        Gets the details entered into the form and convert them into a
        dictionary. Code for date added is from https://www.w3schools.com/
        python/python_datetime.asp
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
            "created_by": "{} {}".format(session['user']['first_name'],
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

        # Updates the product's star ratings in the products database.
        mongo.db.products.update_one(
            {'_id': ObjectId(product_id)},
            star_rating(new_rating=int(request.form.get('overall_rating'))))

        # Adds the review to the reviews database
        mongo.db.reviews.insert_one(review)

        # Redirects to the previous page
        return redirect(url_for('review_details', product_id=product_id))

    # Gets the product's details from the products databse
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})

    if product is None:
        """
        Returns a status of 404 if the product does not exist. Code is
        from https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
        """
        abort(404)

    # Renders the add_review.html template
    return render_template("add_review.html", page_title="Add Review",
                           product_id=product_id)


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
        Gets the details entered into the form and convert them into a
        dictionary. Code for date added is from https://www.w3schools.com/
        python/python_datetime.asp
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

        # Updates the product's feature ratings in the products database
        mongo.db.products.update_one(
            {'_id': product_ratings['_id']}, {"$set": new_ratings})

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
        Updates the review in the reviews database. Code is from https://
        docs.mongodb.com/manual/reference/method/db.collection.updateOne/
        """
        mongo.db.reviews.update_one(
            {'_id': ObjectId(review_id)}, {"$set": review})

        # Redirects to the product's review details page
        return redirect(url_for('review_details',
                                product_id=product_ratings['_id']))

    """
    Gets the review author's details from the reviews database. Code for
    returning selected fields from https://docs.mongodb.com/manual/tutorial/
    project-fields-from-query-results/
    """
    review = mongo.db.reviews.find_one(
        {"_id": ObjectId(review_id)}, {"created_by": 1, "_id": 0})

    if review is None:
        """
        Returns a status of 404 if no review is returned. Code is
        from https://flask.palletsprojects.com/en/1.1.x/patterns
        /errorpages/
        """
        return abort(404)

    elif "{} {}".format(session['user']['first_name'], session['user']
                        ['last_name']) != review['created_by']:
        """
        Returns a status of 403 if the user is not the
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
    """
    Gets the review author's details from the reviews database. Code for
    returning selected fields from https://docs.mongodb.com/manual/tutorial/
    project-fields-from-query-results/
    """
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)}, {
        "created_by": 1, "_id": 0})

    if review is None:
        """
        Returns a 404 status if no review is returned.
        Code is from https://flask.palletsprojects.com/en/1.1.x/
        patterns/errorpages/
        """
        return abort(404)

    elif "{} {}".format(session['user']['first_name'], session['user']
                        ['last_name']) != review['created_by']:
        """
        Returns a status of 403 if the user is not the
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
            {'_id': product_ratings['_id']}, {"$set": new_ratings})

        # Updates the product's star ratings in the products database
        mongo.db.products.update_one({"name": user_ratings['product']},
                                     star_rating(
            prev_rating=user_ratings['overall_rating']))

        # Deletes the review from the reviews database
        mongo.db.reviews.delete_one({"_id": ObjectId(review_id)})

        # Redirects to the product's review details page
        return redirect(url_for('review_details',
                                product_id=product_ratings['_id']))


@app.route("/add_product", methods=["GET", "POST"])
@login_required
@admin_required
def add_product():
    if request.method == "POST":
        """
        Gets the details entered into the form and convert them into a
        dictionary.
        """
        product = request.form.to_dict()

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
        Converts the price to the decimal 128 data type. Code is from https://
        pymongo.readthedocs.io/en/stable/api/bson/decimal128.html
        """
        product['price'] = Decimal128(product['price'])

        # Add the product details to the products database
        mongo.db.products.insert_one(product)

        """
        Adds the brand to the relevant brands list in the categories database.
        Code is from https://docs.mongodb.com/manual/reference/operator/update/
        addToSet/
        """
        mongo.db.categories.update_one({"name": product['category']}, {
                                       "$addToSet": {"brands": product['brand']
                                                     }})

        # Redirects to the product management page
        return redirect(url_for('product_management'))

    # Gets a list of categories from the categories database
    categories = mongo.db.categories.find()

    # Renders the add_product.html template
    return render_template('add_product.html', page_title='Add Product',
                           categories=categories)


@app.route("/edit_product/<product_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_product(product_id):
    if request.method == "POST":
        """
        Gets the details entered into the form and convert them into a
        dictionary.
        """
        product = request.form.to_dict()

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
        Converts the price to the decimal 128 data type. Code is from https://
        pymongo.readthedocs.io/en/stable/api/bson/decimal128.html
        """
        product['price'] = Decimal128(product['price'])

        """
        Adds the product details to the products database
        Code is from https://docs.mongodb.com/manual/reference/
        method/db.collection.updateOne/
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

        # Redirects to the product management page
        return redirect(url_for('product_management'))

    # Gets the product's details from the products databse
    product = mongo.db.products.find_one({'_id': ObjectId(product_id)})

    if product is None:
        """
        Returns a status of 404 if the product does not exist. Code is
        from https://flask.palletsprojects.com/en/1.1.x/patterns/errorpages/
        """
        abort(404)

    # Gets a list of categories from the categories database
    categories = mongo.db.categories.find()

    # Renders the edit_product.html template
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
    """
    Gets the product's name and category. Code for returning selected fields
    is from https://docs.mongodb.com/manual/tutorial
    project-fields-from-query-results/
    """
    product = mongo.db.products.find_one({"_id": ObjectId(product_id)},
                                         {"brand": 1, "category": 1, "_id": 0})

    """
    Counts the number of products in the product's category from the product's
    brand. Code is from https://docs.mongodb.com/manual/reference/method/
    db.collection.count/ and https://docs.mongodb.com/manual/tutorial/
    project-fields-from-query-results/
    """
    brand_count = mongo.db.products.count(
        {"brand": product['brand'], "category": product['category']})

    """
    If the brand count is equal to one, deletes the brand from the relevant
    category's brands array in the categories database. Code is from https://
    docs.mongodb.com/manual/reference/operator/update/pull/
    """
    if brand_count == 1:
        mongo.db.categories.update_one({"name": product['category']}, {
                                       "$pull": {"brands": product['brand']
                                                 }})

    # Deletes the product
    mongo.db.products.delete_one({"_id": ObjectId(product_id)})
    return redirect(url_for('product_management'))


@app.errorhandler(403)
def page_forbidden(e):
    """
    Renders the 403.html template if the HTTP request returns a status of 403.
    Code is from https://flask.palletsprojects.com/en/1.1.x/patterns/
    errorpages/
    """
    return render_template("403.html", page_title=403)


@app.errorhandler(404)
def page_not_found(e):
    """
    Renders the 404.html template if the HTTP request returns a status of 404.
    Code is from https://flask.palletsprojects.com/en/1.1.x/patterns/
    errorpages/
    """
    return render_template("404.html", page_title=404)


app.run(host=os.getenv('IP'), port=int(os.getenv('PORT')), debug=True)
