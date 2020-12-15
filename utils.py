from flask_paginate import Pagination


def create_user_session(user):
    session_file = {
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "user_type": user["user_type"]
    }
    return session_file


def calculate_total_reviews(product):
    total = product['one_star'] + product['two_stars'] + \
        product['three_stars'] + \
        product['four_stars'] + product['five_stars']
    return total


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


def sort_items(sort):
    sort_file = {"a-to-z": [("name", 1)], "z-to-a": [("name", -1)],
                "date-added": [("date_added", -1), ("name", 1)],
                "price": [("price", -1), ("name", 1)], "cat_asc": [("category",
                1)], "cat_desc": [("category", -1)]}
    return sort_file[sort]


def get_price_range(category, value):
    # phone and value
    price_file = {"phones": {1: {"$gte": 0, "$lte": 500}, 2: {"$gte": 500,
                "$lte": 750}, 3:  {"$gte": 750, "$lte": 1000}, 4: {"$gte": 1000}
                }, "tablets": {1: {"$gte": 0, "$lte": 500}, 2: {"$gte": 500,
                "$lte": 750}, 3:  {"$gte": 750, "$lte": 1000}, 4: {"$gte": 1000}
                }, "laptops": {1: {"$gte": 0, "$lte": 750}, 2: {"$gte": 750,
                "$lte": 1000}, 3: {"$gte": 1000, "$lte": 1250}, 4: {"$gte":
                1250, "$lte": 1500}, 5: {"$gte": 1500}}, "accessories": {1:
                {"$gte": 0, "$lte": 200}, 2: {"$gte": 200, "$lte": 300}, 3:
                {"$gte": 300, "$lte": 400}, 4: {"$gte": 400}}, "all": {1:
                {"$gte": 0, "$lte": 250}, 2: {"$gte": 250, "$lte": 500}, 3:
                {"$gte": 500, "$lte": 750}, 4: {"$gte": 750, "$lte": 1000}, 5:
                {"$gte": 1000}}}
    return price_file[category][value]


def calculate_rating(average, total, new_rating, prev_rating, new_total):
    rating = ((average * total) + prev_rating +
              float(new_rating)) / new_total
    rating = round(rating, 1)
    return rating


def product_ratings_query():
    query = {"overall_rating": 1, "performance_rating": 1,
        "usability_rating": 1, "price_rating": 1, "quality_rating": 1,
        "one_star": 1, "two_stars": 1, "three_stars": 1, "four_stars": 1,
        "five_stars": 1, "_id": 0}
    return query


def user_ratings_query():
    query = {"product": 1, "overall_rating": 1, "performance_rating": 1, "usability_rating": 1, "price_rating": 1, "quality_rating": 1, "_id": 0}
    return query

def add_ratings(product_ratings, product_count, form):
    rating = {'overall_rating': calculate_rating(product_ratings[0]
        ['overall_rating'], product_count, 0, int(form['overall_rating']),
        product_count + 1), 'performance_rating': calculate_rating
        (product_ratings[0]['performance_rating'], product_count, 0, int(form
        ['performance_rating']), product_count + 1), 'usability_rating':
        calculate_rating(product_ratings[0]['usability_rating'], 
        product_count, 0, int(form['usability_rating']), product_count + 1), 
        'price_rating': calculate_rating(product_ratings[0]
        ['price_rating'], product_count, 0, int(form['price_rating']),
        product_count + 1), 'quality_rating': calculate_rating
        (product_ratings[0] ['quality_rating'], product_count, 0, int(form
        ['quality_rating']), product_count + 1)
    }
    return rating

def edit_ratings(user_ratings, product_ratings, product_count, form):
    rating = {
        'overall_rating': calculate_rating(product_ratings[0]
        ['overall_rating'], product_count, user_ratings[0]['overall_rating'],
        form['overall_rating'], product_count + 1), 'performance_rating': 
        calculate_rating (product_ratings[0]['performance_rating'], 
        product_count, user_ratings[0]['performance_rating'], form
        ['performance_rating'], product_count + 1), 'usability_rating':
        calculate_rating(product_ratings[0]['usability_rating'], 
        product_count, user_ratings[0]['usability_rating'], form
        ['usability_rating'], product_count + 1), 'price_rating':
        calculate_rating(product_ratings[0]['price_rating'], product_count, 
        user_ratings[0]['price_rating'], form['price_rating'],
        product_count + 1), 'quality_rating': calculate_rating
        (product_ratings[0]['quality_rating'], product_count, user_ratings
        [0]['quality_rating'], form ['quality_rating'], product_count + 1)
    }
    return rating

def delete_ratings(user_ratings, product_ratings, product_count, form):
    rating = {
        'overall_rating': calculate_rating(product_ratings[0]
        ['overall_rating'], product_count, user_ratings[0]['overall_rating'], 0,
        product_count - 1), 'performance_rating': calculate_rating
        (product_ratings[0]['performance_rating'], product_count, user_ratings
        [0]['performance_rating'], 0, product_count - 1), 'usability_rating':
        calculate_rating(product_ratings[0]['usability_rating'], 
        product_count, user_ratings[0]['usability_rating'], 0, product_count - 
        1),'price_rating': calculate_rating(product_ratings[0]
        ['price_rating'], product_count, user_ratings[0]['price_rating'], 0,
        product_count - 1), 'quality_rating': calculate_rating(product_ratings
        [0]['quality_rating'], product_count, user_ratings[0]['quality_rating'],
         0, product_count - 1)
    }
    return rating

def star_rating(new_rating=None, prev_rating=None):
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
