#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This application provides a list of items within a variety of categories
# as well as provide a user registration and authentication system.
# Registered users will have the ability to post, edit and delete their own
# items.
# This web app is a project for the Udacity FSWDN
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash
from flask import make_response
from flask import session as login_session
from sqlalchemy import create_engine, asc, desc, exc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import random
import requests
import string


app = Flask(__name__)

GOOGLE_CLIENT_SECRET = "client_secret.json"
GOOGLE_CLIENT_ID = json.loads(
    open(GOOGLE_CLIENT_SECRET, "r").read())["web"]["client_id"]

# Connect to database and create database session.
engine = create_engine("sqlite:///catalog.db")
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route("/login")
def show_login():
    """Create anti-forgery state token."""
    state = "".join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session["state"] = state
    return render_template("login.html", STATE=state)


@app.route("/gconnect", methods=["POST"])
def gconnect():
    """Google connect."""

    # Validate state token
    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(GOOGLE_CLIENT_SECRET, scope="")
        oauth_flow.redirect_uri = "postmessage"
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps("Failed to upgrade the authorization code."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ("https://www.googleapis.com/oauth2/v1/tokeninfo?"
           "access_token={}").format(access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, "GET")[1])

    # If there was an error in the access token info, abort.
    if result.get("error") is not None:
        response = make_response(json.dumps(result.get("error")), 500)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token["sub"]
    if result["user_id"] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Verify that the access token is valid for this app.
    if result["issued_to"] != GOOGLE_CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers["Content-Type"] = "application/json"
        return response

    stored_access_token = login_session.get("access_token")
    stored_gplus_id = login_session.get("gplus_id")
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps("Current user is already connected."), 200)
        response.headers["Content-Type"] = "application/json"
        return response

    # Store the access token in the session for later use.
    login_session["access_token"] = credentials.access_token
    login_session["gplus_id"] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {"access_token": credentials.access_token, "alt": "json"}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session["username"] = data["name"]
    login_session["picture"] = data["picture"]
    login_session["email"] = data["email"]

    # Add provider to login session.
    login_session["provider"] = "google"

    # See if user exists, if it doesn't make a new one.
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session["user_id"] = user_id

    output = "<h1>Welcome, "
    output += login_session["username"]
    output += "!</h1>"
    output += '<img src="' + login_session["picture"] + '" '
    output += 'style = "width: 300px; height: 300px; border-radius: 150px; '
    output += '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash("You are now logged in as {}.".format(login_session["username"]))
    print("done!")
    return output


@app.route("/gdisconnect")
def gdisconnect():
    """Google disconnect."""
    # Revoke a current user's token and reset their login_session.
    # Only disconnect a connected user.
    access_token = login_session.get("access_token")
    if access_token is None:
        response = make_response(
            json.dumps("Current user not connected."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    url = "https://accounts.google.com/o/oauth2/revoke?token={}".format(
            access_token)
    h = httplib2.Http()
    result = h.request(url, "GET")[0]

    if result["status"] == "200":
        del login_session["access_token"]
        del login_session["gplus_id"]
        del login_session["username"]
        del login_session["email"]
        del login_session["picture"]
        response = make_response(json.dumps("Successfully disconnected."), 200)
        response.headers["Content-Type"] = "application/json"
        return response
    else:
        response = make_response(
            json.dumps("Failed to revoke token for given user.", 400))
        response.headers["Content-Type"] = "application/json"
        return response


@app.route("/fbconnect", methods=["POST"])
def fbconnect():
    """Facebook connect."""
    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    access_token = request.data
    print("Access token received {}.".format(access_token))

    app_id = json.loads(open("fb_client_secrets.json", "r")
                        .read())["web"]["app_id"]
    app_secret = json.loads(
        open("fb_client_secrets.json", "r").read())["web"]["app_secret"]

    url = ("https://graph.facebook.com/oauth/access_token?"
           "grant_type=fb_exchange_token&client_id={}&client_secret={}"
           "&fb_exchange_token={}").format(app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, "GET")[1]

    # Use token to get user info from API.
    # userinfo_url = "https://graph.facebook.com/v2.8/me"
    """
    Due to the formatting for the result from the server token exchange we
    have to split the token first on commas and select the first index which
    gives us the key : value for the server access token then we split it on
    colons to pull out the actual token value and replace the remaining quotes
    with nothing so that it can be used directly in the graph api calls
    """
    token = result.split(",")[0].split(":")[1].replace('"', "")

    url = ("https://graph.facebook.com/v2.8/me?"
           "access_token={}&fields=name,id,email").format(token)
    h = httplib2.Http()
    result = h.request(url, "GET")[1]
    data = json.loads(result)
    login_session["provider"] = "facebook"
    login_session["username"] = data["name"]
    login_session["email"] = data["email"]
    login_session["facebook_id"] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout.
    login_session["access_token"] = token

    # Get user picture.
    url = ("https://graph.facebook.com/v2.8/me/picture?"
           "access_token={}&redirect=0&height=200&width=200").format(token)
    h = httplib2.Http()
    result = h.request(url, "GET")[1]
    data = json.loads(result)

    login_session["picture"] = data["data"]["url"]

    # See if user exists.
    user_id = get_user_id(login_session["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session["user_id"] = user_id

    output = "<h1>Welcome, "
    output += login_session["username"]

    output += "!</h1>"
    output += '<img src="'
    output += login_session["picture"]
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += ' -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as {}.".format(login_session["username"]))
    return output


@app.route("/fbdisconnect")
def fbdisconnect():
    """Facebook disconnect."""
    facebook_id = login_session["facebook_id"]

    # The access token must me included to successfully logout.
    access_token = login_session["access_token"]
    url = "https://graph.facebook.com/{}/permissions?access_token={}".format(
            facebook_id, access_token)
    h = httplib2.Http()
    h.request(url, "DELETE")[1]
    return "You have been logged out."


@app.route("/disconnect")
def disconnect():
    """Disconnect based on provider."""
    login_session["provider"] = "google"

    if "provider" in login_session:
        if login_session["provider"] == "google":
            gdisconnect()
            delete_key_login_session("gplus_id")
            delete_key_login_session("credentials")

        if login_session["provider"] == "facebook":
            fbdisconnect()
            del login_session["facebook_id"]

        delete_key_login_session("username")
        delete_key_login_session("email")
        delete_key_login_session("picture")
        delete_key_login_session("user_id")
        delete_key_login_session("provider")
        flash("You have successfully been logged out.")
        return redirect(url_for("show_categories"))
    else:
        flash("You were not logged in.")
        return redirect(url_for("show_ctegories"))


def delete_key_login_session(key):
    try:
        del login_session[key]
    except:
        print(
            ("An error occured trying to delete login_session "
             "key='{}'.").format(key))


def create_user(login_session):
    """User helper function."""
    newUser = User(name=login_session["username"],
                   email=login_session["email"],
                   picture=login_session["picture"])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session["email"]).first()
    return user.id


def get_user_info(user_id):
    """User helper function."""
    user = session.query(User).filter_by(id=user_id).first()
    return user


def get_user_id(email):
    """User helper function."""
    try:
        user = session.query(User).filter_by(email=email).first()
        return user.id
    except:
        return None


# JSON APIs to view category and item information.
# The first JSON endpoint follows the instructions on page 3 of
# the "Getting Started" guide (https://goo.gl/vrAaoe).
# The second JSON endpoint includes versioning in the URI Path.
# It also uses the plural form as recommended in
# Lesson 18: Writing Developer-Friendly APIs
@app.route("/catalog.json", methods=["GET"])
@app.route("/v1/categories", methods=["GET"])
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


@app.route("/v1/categories/<path:category_name>", methods=["GET"])
def api_get_category(category_name):
    """Return a specific category with his items."""
    category = session.query(Category).filter_by(name=category_name).first()
    if category:
        category = category.serialize
        items = [
            i.serialize for i in session.query(Item).filter_by(
                category_id=category["id"]).all()]
        if items:
            category["Item"] = items
    return jsonify(Category=category)


@app.route(
    "/v1/categories/<path:category_name>/<path:item_title>",
    methods=["GET"])
def api_get_item(category_name, item_title):
    """Return a specific item."""
    category = session.query(Category).filter_by(name=category_name).first()
    if category:
        item = session.query(Item).filter_by(
            category_id=category.id, title=item_title).first()
        if item:
            return jsonify(Item=item.serialize)
    return jsonify(Item=None)


@app.route("/")
@app.route("/catalog")
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


@app.route("/catalog/<path:category_name>")
@app.route("/catalog/<path:category_name>/items")
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


@app.route("/catalog/<path:category_name>/<path:item_title>")
def show_item(category_name, item_title):
    """Show a specific item."""
    category = session.query(Category).filter_by(name=category_name).first()
    item = session.query(Item).filter_by(
        category_id=category.id, title=item_title).first()
    return render_template("show_item.html", item=item)


@app.route("/catalog/items/new", methods=["GET", "POST"])
def new_item():
    """Add a new item without presetting a category."""
    if "username" not in login_session:
        return redirect("/login")
    return new_category_item(None)


@app.route("/catalog/<path:category_name>/items/new", methods=["GET", "POST"])
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
            # flash("Item '{}' Successfully Added".format(item.title))
            return redirect(url_for(
                "show_item", category_name=item.category.name,
                item_title=item.title))
        except exc.IntegrityError:
            session.rollback()
            flash(
                "You can not add this item since another item already "
                " exists in the database with the same title and category.")
            return redirect(url_for("new_item", category_name=category_name))
    else:
        categories = session.query(Category).order_by(asc(Category.name)).all()
        return render_template(
            "new_item.html", categories=categories,
            category_name=category_name)


@app.route(
    "/catalog/<path:category_name>/<path:item_title>/edit",
    methods=["GET", "POST"])
def edit_item(category_name, item_title):
    """Edit a item."""
    if "username" not in login_session:
        return redirect("/login")

    category = session.query(Category).filter_by(name=category_name).first()
    item = session.query(Item).filter_by(
            category_id=category.id, title=item_title).first()

    if request.method == "POST":
        if request.form["title"]:
            item.title = request.form["title"].strip()
        if request.form["description"]:
            item.description = request.form["description"].strip()
        if request.form["category_name"]:
            name = request.form["category_name"].strip()
            category = session.query(Category).filter_by(name=name).first()
            item.category_id = category.id

        try:
            item.update()
            session.add(item)
            session.commit()
            flash("Item '{}' Successfully Edited".format(item.title))
            return redirect(url_for(
                "show_item", category_name=item.category.name,
                item_title=item.title))
        except exc.IntegrityError:
            session.rollback()
            flash(
                "You can not update this item since another item already "
                " exists in the database with the same title and category.")
            item = session.query(Item).filter_by(
                category_id=category.id, title=item_title).first()
            return redirect(url_for(
                "edit_item", category_name=item.category.name,
                item_title=item.title))
    else:
        categories = session.query(Category).order_by(asc(Category.name)).all()
        return render_template(
            "edit_item.html", item=item, categories=categories)


@app.route(
    "/catalog/<path:category_name>/<path:item_title>/delete",
    methods=["GET", "POST"])
def delete_item(category_name, item_title):
    """Delete a item."""
    if "username" not in login_session:
        return redirect("/login")

    category = session.query(Category).filter_by(name=category_name).first()
    item = session.query(Item).filter_by(
            category_id=category.id, title=item_title).first()

    if request.method == "POST":
        session.delete(item)
        session.commit()
        flash("Item '{}' Successfully Deleted".format(item.title))
        return redirect(url_for("show_items", category_name=category_name))
    else:
        return render_template("delete_item.html", item=item)


@app.route("/catalog/about")
def about():
    """Show about page."""
    return render_template("about.html")


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
