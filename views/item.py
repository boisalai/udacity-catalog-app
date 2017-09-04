#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from flask import Blueprint, request, render_template, redirect
from flask import url_for, flash
from flask import session as login_session
from sqlalchemy import asc, exc
from models.category import Category
from models.item import Item
from database import session
from functools import wraps

item = Blueprint('item', __name__)


def login_required(f):
    """Decorator to redirect user if he or she is not logged."""
    @wraps(f)
    def wrapper(*args, **kwds):
        if "username" not in login_session:
            return redirect("/login")
        return f(*args, **kwds)
    return wrapper


def owner_permission(f):
    """Decorator to make sure the user owns an item
       before allowing them to edit or delete it.
    """
    @wraps(f)
    def wrapper(*args, **kwds):
        category_name = kwds["category_name"]
        item_title = kwds["item_title"]

        # Redirect user if category or item does not exist.
        category = session.query(Category).filter_by(
            name=category_name).one_or_none()
        if not category:
            flash("An error occurred. Please try again.", "warning")
            return redirect("/catalog")

        item = session.query(Item).filter_by(
            category_id=category.id, title=item_title).one_or_none()
        if not item:
            flash("An error occurred. Please try again.", "warning")
            return redirect("/catalog/{}/items".format(category_name))

        # Make sure the user owns an item before allowing them to edit
        # or delete it.
        if "username" not in login_session\
                or "user_id" in login_session\
                and item.user_id != login_session["user_id"]:
            flash("You are not allowed to edit or delete this item. "
                  "It belongs to {}.".format(item.user.name), "warning")
            return render_template("show_item.html", item=item)

        kwds['item'] = item
        return f(*args, **kwds)
    return wrapper


@item.route("/catalog/<path:category_name>")
@item.route("/catalog/<path:category_name>/items")
def show_items(category_name):
    """Show a category and all of his items."""
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter_by(name=category_name).one_or_none()
    items = session.query(Item).filter_by(category_id=category.id).all()

    if len(items) < 2:
        title = "{} Item ({} item)"
    else:
        title = "{} Items ({} items)"

    return render_template(
        "categories.html",
        items_title=title.format(category.name, len(items)),
        categories=categories,
        category=category,
        items=items)


@item.route("/catalog/<path:category_name>/<path:item_title>")
def show_item(category_name, item_title):
    """Show a specific item."""
    category = session.query(Category).filter_by(name=category_name).one_or_none()
    item = session.query(Item).filter_by(
        category_id=category.id, title=item_title).one_or_none()
    return render_template("show_item.html", item=item)


@login_required
@item.route("/catalog/items/new", methods=["GET", "POST"])
def new_item():
    """Add a new item without presetting a category."""
    return new_category_item(None)


@login_required
@item.route("/catalog/<path:category_name>/items/new", methods=["GET", "POST"])
def new_category_item(category_name):
    """Add a new item."""
    if request.method == "POST":
        item = Item()
        if request.form["title"]:
            item.title = request.form["title"].strip()
        if request.form["description"]:
            item.description = request.form["description"].strip()
        if request.form["category_name"]:
            category_name = request.form["category_name"].strip()
            category = session.query(Category).filter_by(
                        name=category_name).one_or_none()
            item.category_id = category.id

        try:
            item.user_id = login_session["user_id"]
            session.add(item)
            session.commit()
            flash("Item '{}' Successfully Added".format(item.title), "success")
            return redirect(url_for(
                "item.show_item", category_name=item.category.name,
                item_title=item.title))
        except exc.IntegrityError:
            session.rollback()
            flash(
                "You can not add this item since another item already "
                " exists in the database with the same title and category.",
                "warning")
            return redirect(url_for(
                "item.new_item", category_name=category_name))
    else:
        categories = session.query(Category).order_by(
                        asc(Category.name)).all()
        return render_template(
            "new_item.html", categories=categories,
            category_name=category_name)


@item.route(
    "/catalog/<path:category_name>/<path:item_title>/edit",
    methods=["GET", "POST"])
@login_required
@owner_permission
def edit_item(category_name, item_title, item=None):
    """Edit a item."""
    if request.method == "POST":
        if request.form["title"]:
            item.title = request.form["title"].strip()

        if not item.title:
            flash("Please enter a title.", "warning")
            categories = session.query(Category).order_by(
                            asc(Category.name)).all()
            return render_template(
                "edit_item.html", item=item, categories=categories)

        if request.form["description"]:
            item.description = request.form["description"].strip()

        if request.form["category_name"]:
            name = request.form["category_name"].strip()
            category = session.query(Category).filter_by(name=name).one_or_none()
            if category:
                item.category_id = category.id
            else:
                flash("Please select a category.", "warning")
                categories = session.query(Category).order_by(
                            asc(Category.name)).all()
                return render_template(
                    "edit_item.html", item=item, categories=categories)

        try:
            item.update()
            session.add(item)
            session.commit()
            flash(
                "Item '{}' Successfully Edited".format(item.title),
                "success")
            return redirect(url_for(
                "item.show_item", category_name=item.category.name,
                item_title=item.title))
        except exc.IntegrityError:
            session.rollback()
            flash(
                "You can not update this item since another item already "
                " exists in the database with the same title and category.",
                "warning", "warning")
            item = session.query(Item).filter_by(
                category_id=category.id, title=item_title).one_or_none()
            return redirect(url_for(
                "item.edit_item", category_name=item.category.name,
                item_title=item.title))
    else:
        categories = session.query(Category).order_by(
                        asc(Category.name)).all()
        return render_template(
            "edit_item.html", item=item, categories=categories)


@item.route(
    "/catalog/<path:category_name>/<path:item_title>/delete",
    methods=["GET", "POST"])
@login_required
@owner_permission
def delete_item(category_name, item_title, item=None):
    """Delete a item."""
    if request.method == "POST":
        session.delete(item)
        session.commit()
        flash("Item '{}' Successfully Deleted".format(item.title), "success")
        return redirect(
            url_for("item.show_items", category_name=category_name))
    else:
        return render_template("delete_item.html", item=item)
