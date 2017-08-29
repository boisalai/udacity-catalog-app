#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from flask import Blueprint, request, render_template, redirect
from flask import url_for, flash
from flask import session as login_session
from sqlalchemy import asc, exc
from models import Category, Item
from database import session

item = Blueprint('item', __name__)


@item.route("/catalog/<path:category_name>")
@item.route("/catalog/<path:category_name>/items")
def show_items(category_name):
    """Show a category and all of his items."""
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter_by(name=category_name).first()
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
    category = session.query(Category).filter_by(name=category_name).first()
    item = session.query(Item).filter_by(
        category_id=category.id, title=item_title).first()
    return render_template("show_item.html", item=item)


@item.route("/catalog/items/new", methods=["GET", "POST"])
def new_item():
    """Add a new item without presetting a category."""
    if "username" not in login_session:
        return redirect("/login")
    return new_category_item(None)


@item.route("/catalog/<path:category_name>/items/new", methods=["GET", "POST"])
def new_category_item(category_name):
    """Add a new item."""
    if "username" not in login_session:
        return redirect("/login")

    if request.method == "POST":
        item = Item()
        if request.form["title"]:
            item.title = request.form["title"].strip()
        if request.form["description"]:
            item.description = request.form["description"].strip()
        if request.form["category_name"]:
            category_name = request.form["category_name"].strip()
            category = session.query(Category).filter_by(
                        name=category_name).first()
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
def edit_item(category_name, item_title):
    """Edit a item."""
    if "username" not in login_session:
        return redirect("/login")

    category = session.query(Category).filter_by(name=category_name).first()
    if category:
        item = session.query(Item).filter_by(
                category_id=category.id, title=item_title).first()

    if not item:
        flash("An error occurred. Please try again.", "warning")
        categories = session.query(Category).order_by(
                        asc(Category.name)).all()
        return render_template(
            "edit_item.html", item=item, categories=categories)
    
    # 20170829: We must make sure the user owns an item before allowing 
    # them to edit it.
    if item.user_id != login_session["user_id"]:
        flash("You are not allowed to edit this item. "
              "It belongs to {{ item.user.name }}.", "warning")
        categories = session.query(Category).order_by(
                        asc(Category.name)).all()
        return render_template(
            "edit_item.html", item=item, categories=categories)

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
            category = session.query(Category).filter_by(name=name).first()
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
                category_id=category.id, title=item_title).first()
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
def delete_item(category_name, item_title):
    """Delete a item."""
    if "username" not in login_session:
        return redirect("/login")

    category = session.query(Category).filter_by(name=category_name).first()
    item = session.query(Item).filter_by(
            category_id=category.id, title=item_title).first()

    # 20170829: We must make sure the user owns an item before allowing 
    # them to delete it.
    if item.user_id != login_session["user_id"]:
        flash("You are not allowed to delete this item. "
              "It belongs to {{ item.user.name }}.", "warning")
        return render_template("show_item.html", item=item)

    if request.method == "POST":
        session.delete(item)
        session.commit()
        flash("Item '{}' Successfully Deleted".format(item.title), "success")
        return redirect(
            url_for("item.show_items", category_name=category_name))
    else:
        return render_template("delete_item.html", item=item)
