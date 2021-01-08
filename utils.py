from flask_paginate import Pagination


def create_user_session(user):
    """ Function to add the user's details to the session cookie """
    session_file = {
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "user_type": user["user_type"]
    }
    return session_file


def paginate_items(items, offset, per_page):
    """
    Function to set the pagination perameters. Code is from https://
    gist.github.com/mozillazg/69fb40067ae6d80386e10e105e6803c9
    """
    return items[offset: offset + per_page]


def paginate(items, page, per_page):
    """
    Function to paginate the items. Code is from https://gist.github.com/
    mozillazg/69fb40067ae6d80386e10e105e6803c9
    """
    total = len(items)
    return Pagination(
        page=page,
        per_page=per_page,
        total=total,
        css_framework='bootstrap4'
    )


def get_price_range(category, value):
    """
    Function to generate the price query. Code is from https://docs.mongodb.com
    /manual/reference/operator/aggregation/gte/ and https://docs.mongodb.com/
    manual/reference/operator/aggregation/lte/
    """
    price_file = {'Phones': {
        1: {'$gte': 0, '$lte': 500},
        2: {'$gte': 500, '$lte': 750},
        3: {'$gte': 750, '$lte': 1000},
        4: {'$gte': 1000},
    },
        'Tablets': {
        1: {'$gte': 0, '$lte': 500},
        2: {'$gte': 500, '$lte': 750},
        3: {'$gte': 750, '$lte': 1000},
        4: {'$gte': 1000},
    },
        'Laptops': {
        1: {'$gte': 0, '$lte': 750},
        2: {'$gte': 750, '$lte': 1000},
        3: {'$gte': 1000, '$lte': 1250},
        4: {'$gte': 1250, '$lte': 1500},
        5: {'$gte': 1500},
    },
        'Accessories': {
        1: {'$gte': 0, '$lte': 200},
        2: {'$gte': 200, '$lte': 300},
        3: {'$gte': 300, '$lte': 400},
        4: {'$gte': 400},
    },
        'All': {
        1: {'$gte': 0, '$lte': 250},
        2: {'$gte': 250, '$lte': 500},
        3: {'$gte': 500, '$lte': 750},
        4: {'$gte': 750, '$lte': 1000},
        5: {'$gte': 1000},
    }}
    return price_file[category][value]


def search(query, category):
    """
    Function to genrate the get products search query. In method is from
    https://docs.mongodb.com/manual/reference/operator/aggregation/in/
    """

    query_file = {}

    if query.get('search'):
        query_file["$text"] = {"$search": query['search']}

    if query.get('categories'):
        categories = query['categories'].split(",")
        query_file['category'] = {"$in": categories}

    if query.get('price'):
        query_file["price"] = get_price_range(
            category, int(query['price']))

    if query.get('brands'):
        brands = query['brands'].split(",")
        query_file["brand"] = {"$in": brands}

    return query_file


def sort_items(sort=None):
    """
    Function to generate the sort query. Code is from https://stackoverflow.com
    questions/8109122/how-to-sort-mongodb-with-pymongo
    """
    sort_file = {
        'featured': [('_id', 1)],
        'date-added': [('date_added', -1), ('name', 1)],
        'price-asc': [('price', 1), ('name', 1)],
        'price-desc': [('price', -1), ('name', 1)],
        'rating': [('overall_rating', -1), ('name', 1)],
        'cat_asc': [('category', 1)],
        'cat_desc': [('category', -1)],
        'a-to-z': [('name', 1)],
        'z-to-a': [('name', -1)],
    }
    if sort:
        return sort_file[sort]

    else:
        return sort_file['featured']


def product_ratings_query():
    """
    Function to generate the get product ratings search query. Code is from
    https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/
    """
    query = {
        'name': 1,
        'overall_rating': 1,
        'performance_rating': 1,
        'usability_rating': 1,
        'price_rating': 1,
        'quality_rating': 1,
        'one_star': 1,
        'two_stars': 1,
        'three_stars': 1,
        'four_stars': 1,
        'five_stars': 1,
    }

    return query


def user_ratings_query():
    """
    Function to generate the get user ratings search query. Code is from
    https://docs.mongodb.com/manual/tutorial/project-fields-from-query-results/
    """
    query = {
        'product': 1,
        'overall_rating': 1,
        'performance_rating': 1,
        'usability_rating': 1,
        'price_rating': 1,
        'quality_rating': 1,
        '_id': 0,
    }

    return query


def calculate_rating(average, total, new_rating, prev_rating, new_total):
    """
    Function to calculate the product's new rating. Round method is from
    https://www.programiz.com/python-programming/methods/built-in/round
    """
    rating = ((average * total) - prev_rating +
              float(new_rating)) / new_total
    rating = round(rating, 1)
    return rating


def add_ratings(product_ratings, product_count, form):
    """
    Function to calculate the product's new ratings for when a review is added
    """
    rating = {
        'overall_rating': calculate_rating(product_ratings['overall_rating'],
        product_count, 0, int(form['overall_rating']), product_count + 1),
        'performance_rating': calculate_rating(product_ratings
        ['performance_rating'], product_count, 0, int(form['performance_rating'
        ]), product_count + 1), 'usability_rating': calculate_rating
        (product_ratings['usability_rating'], product_count, 0, int(form
        ['usability_rating']), product_count + 1), 'price_rating':
        calculate_rating(product_ratings['price_rating'], product_count, 0, int
        (form['price_rating']), product_count + 1), 'quality_rating':
        calculate_rating(product_ratings['quality_rating'], product_count, 0,
        int(form['quality_rating']), product_count + 1)
    }

    return rating


def edit_ratings(user_ratings, product_ratings, product_count, form):
    """
    Function to calculate the product's new ratings for when a review is edited
    """
    rating = {
        'overall_rating': calculate_rating(product_ratings['overall_rating'],
        product_count, user_ratings['overall_rating'], form['overall_rating'],
        product_count + 1), 'performance_rating': calculate_rating
        (product_ratings['performance_rating'], product_count, user_ratings
        ['performance_rating'], form['performance_rating'], product_count + 1),
        'usability_rating': calculate_rating(product_ratings['usability_rating']
        , product_count, user_ratings['usability_rating'], form
        ['usability_rating'], product_count + 1), 'price_rating':
        calculate_rating(product_ratings['price_rating'], product_count,
        user_ratings['price_rating'], form['price_rating'], product_count + 1),
        'quality_rating': calculate_rating(product_ratings['quality_rating'],
        product_count, user_ratings['quality_rating'], form['quality_rating'],
        product_count + 1)
    }
    return rating


def delete_ratings(user_ratings, product_ratings, product_count):
    """
    Function to calculate the product's new ratings for when a review is
    deleted
    """
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
    Generates the query to update the product's star ratings. Inc method is
    from https://docs.mongodb.com/manual/reference/operator/update/inc/
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
