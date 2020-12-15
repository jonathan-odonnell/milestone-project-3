from flask_paginate import Pagination


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


def add_rating(productRating, newUserRating, totalProductRatings):
    rating = ((productRating * totalProductRatings) +
              float(newUserRating)) / (totalProductRatings + 1)
    rating = round(rating, 1)
    return rating


def product_ratings_query(product):
    query = {"name": product}, {"overall_rating": 1, "performance_rating": 1,
        "usability_rating": 1, "price_rating": 1, "quality_rating": 1,
        "one_star": 1, "two_stars": 1, "three_stars": 1, "four_stars": 1,
        "five_stars": 1, "_id": 0}
    return query


def user_ratings_query(id):
    query = {{"_id": id},
        {"overall_rating": 1, "performance_rating": 1, "usability_rating": 1, "price_rating": 1, "quality_rating": 1, "_id": 0}}
    return query


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
    elif star_rating == 2:
        new_ratings['two_stars'] = prev_ratings[0]['two_stars'] + 1
    elif star_rating == 3:
        new_ratings['three_stars'] = prev_ratings[0]['three_stars'] + 1
    elif star_rating == 4:
        new_ratings['four_stars'] = prev_ratings[0]['four_stars'] + 1
    else:
        new_ratings['five_stars'] = prev_ratings[0]['five_stars'] + 1


def remove_star_rating(star_rating, prev_ratings, new_ratings):
    if star_rating == 1:
        new_ratings['one_star'] = prev_ratings[0]['one_star'] - 1
    elif star_rating == 2:
        new_ratings['two_stars'] = prev_ratings[0]['two_stars'] - 1
    elif star_rating == 3:
        new_ratings['three_stars'] = prev_ratings[0]['three_stars'] - 1
    elif star_rating == 4:
        new_ratings['four_stars'] = prev_ratings[0]['four_stars'] - 1
    else:
        new_ratings['five_stars'] = prev_ratings[0]['five_stars'] - 1
