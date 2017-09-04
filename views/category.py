#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from flask import Blueprint, render_template
from sqlalchemy import asc, desc
from models.category import Category
from models.item import Item
from database import session

category = Blueprint('category', __name__)


@category.route("/")
@category.route("/catalog")
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
