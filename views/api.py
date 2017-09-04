#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from flask import Blueprint, jsonify
from models.category import Category
from models.item import Item
from database import session

api = Blueprint('api', __name__)


# JSON APIs to view category and item information.
# The first JSON endpoint follows the instructions on page 3 of
# the "Getting Started" guide (https://goo.gl/vrAaoe).
# The second JSON endpoint includes versioning in the URI Path.
# It also uses the plural form as recommended in
# Lesson 18: Writing Developer-Friendly APIs
@api.route("/catalog.json", methods=["GET"])
@api.route("/v1/categories", methods=["GET"])
def api_get_categories():
    """Return all categories with their items."""
    categories = [c.serialize for c in session.query(Category).all()]
    for c in range(len(categories)):
        items = [
            i.serialize for i in session.query(Item).filter_by(
                category_id=categories[c]["id"]).all()]
        if items:
            categories[c]["Item"] = items
    return jsonify(Category=categories)


@api.route("/v1/categories/<path:category_name>", methods=["GET"])
def api_get_category(category_name):
    """Return a specific category with his items."""
    category = session.query(Category).filter_by(name=category_name).one_or_none()
    if category:
        category = category.serialize
        items = [
            i.serialize for i in session.query(Item).filter_by(
                category_id=category["id"]).all()]
        if items:
            category["Item"] = items
    return jsonify(Category=category)


@api.route(
    "/v1/categories/<path:category_name>/<path:item_title>",
    methods=["GET"])
def api_get_item(category_name, item_title):
    """Return a specific item."""
    category = session.query(Category).filter_by(name=category_name).one_or_none()
    if category:
        item = session.query(Item).filter_by(
            category_id=category.id, title=item_title).one_or_none()
        if item:
            return jsonify(Item=item.serialize)
    return jsonify(Item=None)
