from flask_paginate import Pagination


def create_user_session(user):
    # Adds the user's details to the session cookie
    session_file = {
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "user_type": user["user_type"]
    }
    return session_file


def paginate_products(products, offset, per_page):
    """
    Sets the pagination perameters. Code is from https://gist.github.com/
    mozillazg/69fb40067ae6d80386e10e105e6803c9
    """
    return products[offset: offset + per_page]


def paginate(products, page, per_page):
    """
    Paginates the products. Code is from https://gist.github.com/
    mozillazg/69fb40067ae6d80386e10e105e6803c9
    """
    total = len(products)
    return Pagination(
        page=page,
        per_page=per_page,
        total=total,
        css_framework='bootstrap4'
    )


def get_price_range(category, value):
    """
    Generates the price query. Code is from https://docs.mongodb.com/manual/
    reference/operator/aggregation/gte/ and https://docs.mongodb.com/manual/
    reference/operator/aggregation/lte/
    """
    price_file = {"Phones": {1: {"$gte": 0, "$lte": 500}, 2: {"$gte": 500,
                "$lte": 750}, 3:  {"$gte": 750, "$lte": 1000}, 4: {"$gte": 1000}
                }, "Tablets": {1: {"$gte": 0, "$lte": 500}, 2: {"$gte": 500,
                "$lte": 750}, 3:  {"$gte": 750, "$lte": 1000}, 4: {"$gte": 1000}
                }, "Laptops": {1: {"$gte": 0, "$lte": 750}, 2: {"$gte": 750,
                "$lte": 1000}, 3: {"$gte": 1000, "$lte": 1250}, 4: {"$gte":
                1250, "$lte": 1500}, 5: {"$gte": 1500}}, "Accessories": {1:
                {"$gte": 0, "$lte": 200}, 2: {"$gte": 200, "$lte": 300}, 3:
                {"$gte": 300, "$lte": 400}, 4: {"$gte": 400}}, "All": {1:
                {"$gte": 0, "$lte": 250}, 2: {"$gte": 250, "$lte": 500}, 3:
                {"$gte": 500, "$lte": 750}, 4: {"$gte": 750, "$lte": 1000}, 5:
                {"$gte": 1000}}}
    return price_file[category][value]


def search(query):
    # Genrates the get products search query
    query_file = {}

    if "search" in query:
        query_file["$text"] = {"$search": query['search']}

    if query['category'] != "all":
        query_file['category'] = query['category']

    if "price" in query:
        query_file["price"] = get_price_range(query['category'], int(query['price']))

    if "brands" in query:
        brands = query['brands'].split(",")
        """
        Code is from https://docs.mongodb.com/manual/reference/operator/
        aggregation/in/
        """
        query_file["brand"] = {"$in": brands}

    return query_file


def sort_items(sort=None):
    """
    Generates the sort query. Code is from https://stackoverflow.com/questions/
    8109122/how-to-sort-mongodb-with-pymongo
    """
    sort_file = {"a-to-z": [("name", 1)], "z-to-a": [("name", -1)],
                 "date-added": [("date_added", -1), ("name", 1)],
                 "price": [("price", -1), ("name", 1)], "cat_asc": [("category",
                 1)], "cat_desc": [("category", -1)]}
    if sort:
        return sort_file[sort]

    else:
        return sort_file['a-to-z']


def product_ratings_query():
    """
    Generates the get product ratings search query. Code is from https://
    docs.mongodb.com/manual/tutorial/project-fields-from-query-results/
    """
    query = {"overall_rating": 1, "performance_rating": 1,
             "usability_rating": 1, "price_rating": 1, "quality_rating": 1,
             "one_star": 1, "two_stars": 1, "three_stars": 1, "four_stars": 1,
             "five_stars": 1, "_id": 0}
    return query


def user_ratings_query():
    """
    Generates the get user ratings search query. Code is from
    https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/
    """
    query = {"product": 1, "overall_rating": 1, "performance_rating": 1,
             "usability_rating": 1, "price_rating": 1, "quality_rating": 1, "_id": 0}
    return query


def calculate_rating(average, total, new_rating, prev_rating, new_total):
    """
    Calculates the product's new rating. Round function is from https://
    www.programiz.com/python-programming/methods/built-in/round
    """
    rating = ((average * total) + prev_rating +
              float(new_rating)) / new_total
    rating = round(rating, 1)
    return rating


def add_ratings(product_ratings, product_count, form):
    # Calculates the product's new ratings for when a review is added
    rating = {
        'overall_rating': calculate_rating(product_ratings ['overall_rating'], 
        product_count, 0, int(form['overall_rating']), product_count + 1), 
        'performance_rating': calculate_rating(product_ratings['performance_rating'], product_count, 0, int(form['performance_rating']
        ), product_count + 1), 'usability_rating': calculate_rating
        (product_ratings['usability_rating'], product_count, 0, int(form
        ['usability_rating']), product_count + 1), 'price_rating': 
        calculate_rating(product_ratings['price_rating'], product_count, 0, int
        (form['price_rating']), product_count + 1), 'quality_rating': 
        calculate_rating(product_ratings['quality_rating'], product_count, 0, 
        int(form['quality_rating']), product_count + 1)
              }
    return rating


def edit_ratings(user_ratings, product_ratings, product_count, form):
    # Calculates the product's new ratings for when a review is edited
    rating = {
        'overall_rating': calculate_rating(product_ratings['overall_rating'], 
        product_count, user_ratings['overall_rating'], form['overall_rating'], 
        product_count + 1), 'performance_rating': calculate_rating
        (product_ratings['performance_rating'], product_count, user_ratings
        ['performance_rating'], form ['performance_rating'], product_count + 1),
        'usability_rating': calculate_rating(product_ratings['usability_rating']
        , product_count, user_ratings['usability_rating'], form
        ['usability_rating'], product_count + 1), 'price_rating': 
        calculate_rating(product_ratings['price_rating'], product_count, 
        user_ratings['price_rating'], form['price_rating'], product_count + 1), 
        'quality_rating': calculate_rating (product_ratings['quality_rating'], 
        product_count, user_ratings ['quality_rating'], form['quality_rating'], 
        product_count + 1)
    }
    return rating


def delete_ratings(user_ratings, product_ratings, product_count):
    # Calculates the product's new ratings for when a review is deleted
    rating = {
        'overall_rating': calculate_rating(product_ratings['overall_rating'], 
        product_count, user_ratings['overall_rating'], 0, product_count - 1), 
        'performance_rating': calculate_rating(product_ratings
        ['performance_rating'], product_count, user_ratings
        ['performance_rating'], 0, product_count - 1), 'usability_rating': 
        calculate_rating(product_ratings['usability_rating'], product_count, 
        user_ratings['usability_rating'], 0, product_count - 1), 
        'price_rating': calculate_rating(product_ratings['price_rating'], 
        product_count, user_ratings['price_rating'], 0, product_count - 1), 
        'quality_rating': calculate_rating(product_ratings['quality_rating'], 
        product_count, user_ratings['quality_rating'], 0, product_count - 1)
    }
    return rating


def star_rating(new_rating=None, prev_rating=None):
    """
    Generates the query to update the product's star ratings. Code is from
    https://docs.mongodb.com/manual/reference/operator/update/inc/
    """
    add_file = {
        1: {"one_star": 1},
        2: {"two_stars": 1},
        3: {"three_stars": 1},
        4: {"four_stars": 1},
        5: {"five_stars": 1}
    }

    delete_file = {
        1: {"one_star": -1},
        2: {"two_stars": -1},
        3: {"three_stars": -1},
        4: {"four_stars": -1},
        5: {"five_stars": -1}
    }

    if new_rating and prev_rating:
        return {"$inc": {add_file[new_rating], delete_file[prev_rating]}}

    elif new_rating:
        return {"$inc": add_file[new_rating]}

    else:
        return {"$inc": delete_file[prev_rating]}
