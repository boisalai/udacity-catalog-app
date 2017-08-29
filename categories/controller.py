#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from flask import Blueprint
from models import Category, Item

categories = Blueprint('categories', __name__)


@categories.route("/")
@categories.route("/catalog")
def show_categories():
    """Show all current categories with the latest added items."""
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(Item).order_by(
                desc(Item.created_date)).limit(10).all()
    return render_template(
        "categories.html",
        items_title="Latest items",
        categories=categories,
        category=None,
        items=items)
