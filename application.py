#!/usr/bin/env python3
#
# Reporting tool that prints out reports (in plain text) based on the
# data in the database.

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item
from flask import session as login_session
import random
import string

# IMPORTS FOR THIS STEP
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open("client_secrets.json", "r").read())["web"]["client_id"]
APPLICATION_NAME = "Catalog App"
DATABASE_NAME = "catalog.db"

# Connect to Database and create database session
engine = create_engine("sqlite:///" + DATABASE_NAME)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Create anti-forgery state token.
@app.route("/login")
def show_login():
    state = "".join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session["state"] = state
    return render_template("login.html", STATE = state)

# Google connect.
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = get_user_id(data["email"])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("done!")
    return output

# Google disconnect.
# Revoke a current user's token and reset their login_session.
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Facebook connect.
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = get_user_id(login_session['email'])
    if not user_id:
        user_id = create_user(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output

# Facebook disconnect.
@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    print("L436 disconnect")
    login_session['provider'] = 'google'
    print(login_session)
    #gdisconnect()
    #del login_session['username']
    #del login_session['provider']

    if 'provider' in login_session:
        print("L439")
        if login_session['provider'] == 'google':
            gdisconnect()
            #del login_session['gplus_id']
            delete_key_login_session('gplus_id')
            #del login_session['credentials']
            delete_key_login_session('credentials')
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
        # del login_session['username']
        delete_key_login_session('username')
        # del login_session['email']
        delete_key_login_session('email')
        # del login_session['picture']
        delete_key_login_session('picture')
        # del login_session['user_id']
        delete_key_login_session('user_id')
        # del login_session['provider']
        delete_key_login_session('provider')
        flash("You have successfully been logged out.")
        return redirect(url_for('show_categories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('show_ctegories'))

def delete_key_login_session(key):
    try: 
        del login_session[key]
    except:
        print("An error occured trying to delete login_session key='%s'." % key)


# User Helper Functions.
def create_user(login_session):
    newUser = User(name = login_session["username"], 
                   email = login_session["email"], 
                   picture = login_session["picture"])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session["email"]).one()
    return user.id

def get_user_info(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def get_user_id(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


# JSON APIs to view category and item information.
@app.route("/api/v1/catalog", methods = ['GET'])
def api_get_categories():
    """Return all categories."""
    categories = session.query(Category).all()
    return jsonify(categories=[i.serialize for i in categories])

@app.route("/api/v1/catalog/<path:category_name>", methods = ['GET'])
def api_get_category(category_name):
    """Return a category."""
    category = session.query(Category).filter_by(id = category_id).one()
    return jsonify(category=category.serialize)

@app.route("/api/v1/catalog/<path:category_name>/items", methods = ['GET'])
def api_get_items(category_name):
    """Return all items of a specific category."""
    items = session.query(Item).filter_by(category_id = category_id).all()
    return jsonify(items=[i.serialize for i in items])

@app.route("/api/v1/catalog/<path:category_name>/<path:item_title>", methods = ['GET'])
def api_get_item(category_name, item_title):
    """Return a item."""
    item = session.query(Item).filter_by(id = item_id).one()
    return jsonify(Item=item.serialize)


@app.route("/")
@app.route("/catalog")
def show_categories():
    print("L343")
    """Show all current categories with the latest added items."""
    categories = session.query(Category).order_by(asc(Category.name)).all()
    items = session.query(Item).order_by(desc(Item.created_date)).limit(10).all()
    return render_template(
        "categories.html", 
        title = APPLICATION_NAME, 
        categories_title = "Categories",
        items_title = "Latest items",
        categories = categories, 
        items = items)

# Show a category and all items for that category.
@app.route("/catalog/<path:category_name>")
@app.route("/catalog/<path:category_name>/items")
def show_items(category_name):
    """Show a category and all items for the given category name."""
    categories = session.query(Category).order_by(asc(Category.name)).all()
    category = session.query(Category).filter_by(name = category_name).one()
    items = session.query(Item).filter_by(category_id = category.id).all()
    creator = get_user_info(category.user_id)
    return render_template(
        "categories.html", 
        title = APPLICATION_NAME,
        categories_title = "Categories",
        items_title = "{} items ({} items)".format(category.name, len(items)),
        categories = categories, 
        category = category, 
        items = items, 
        creator = creator)

# Add a new category.
# TODO
@app.route("/catalog/new", methods = ["GET", "POST"])
def new_category():
    """Add a new category."""
    if "username" not in login_session:
        return redirect("/login")
    if request.method == "POST":
        newCategory = Category(name = request.form["name"].strip(),
            user_id = login_session["user_id"])
        session.add(newCategory)
        session.commit()
        flash("New Category '%s' Successfully Created" % newCategory.name)
        return redirect(url_for("show_categories"))
    else:
        return render_template("new_category.html", 
            title = "Add a new category")

# Edit a category.
# TODO
@app.route("/catalog/<path:category_name>/edit", methods = ["GET", "POST"])
def edit_category(category_name):
    """Edit a category."""
    if "username" not in login_session:
        return redirect("/login")

    editedCategory = session.query(Category).filter_by(id=category_id).one()
    if editedCategory.user_id != login_session["user_id"]:
        return ("<script>function myFunction() { alert('You are not "
                "authorized to edit this category.'); }</script>"
                "<body onload='myFunction()'>")

    if request.method == "POST":
        if request.form["name"]:
            editedCategory.name = request.form["name"].strip()
        session.add(editedCategory)
        session.commit()
        flash("Category '%s' Successfully Edited" % editedCategory.name)
        return redirect(url_for("show_categories"))
    else:
        return render_template("edit_category.html", 
            title = "Edit a category", category_id = category_id, item = editedCategory)

# Delete a category.
# TODO
@app.route("/catalog/<path:category_name>/delete", methods = ["GET", "POST"])
def delete_category(category_name):
    """Delete a category."""
    if "username" not in login_session:
        return redirect("/login")
    
    itemToDelete = session.query(Category).filter_by(id=category_id).one()
    if itemToDelete.user_id != login_session["user_id"]:
        return ("<script>function myFunction() { alert('You are not "
                "authorized to delete this category.'); }</script>"
                "<body onload='myFunction()'>")

    if request.method == "POST":
        session.delete(itemToDelete)
        session.commit()
        flash("Category '%s' Successfully Deleted" % itemToDelete.name)
        return redirect(url_for("show_categories"))
    else:
        return render_template("delete_category.html", 
            title = itemToDelete.name, category_id = category_id)

# Show a specifiq item.
# See "Handling URLs containing slash '/' character"
# (http://flask.pocoo.org/snippets/76/)
@app.route("/catalog/<path:category_name>/<path:item_title>")
def show_item(category_name, item_title):
    """Show a specific item."""
    category = session.query(Category).filter_by(name = category_name).one()
    item = session.query(Item).filter_by(category_id = category.id, title = item_title).first()
    creator = get_user_info(category.user_id)
    return render_template("item.html", 
        title = APPLICATION_NAME, 
        category = category, 
        item = item, 
        creator = creator)

# Add a new item.
@app.route("/catalog/<path:category_name>/new", methods = ["GET", "POST"])
def new_item(category_name):
    """Add a new item."""
    if "username" not in login_session:
        return redirect("/login")
    if request.method == "POST":
        category = session.query(Category).filter_by(id = category_id).one()
        newItem = Item(
                name = request.form["name"].strip(), 
                description = request.form["description"].strip(), 
                price = request.form["price"].strip(), 
                course = request.form["course"].strip(), 
                category_id = category_id,
                user_id = category.user_id)
        session.add(newItem)
        session.commit()
        flash("New Item Item '%s' Created" % newItem.name)
        return redirect(url_for("showItem", category_id = category_id))
    else:
        return render_template("newItem.html", 
            title = "Add a new item", category_id = category_id)

# Edit a item.
@app.route("/catalog/<path:category_name>/<path:item_title>/edit", methods = ["GET", "POST"])
def edit_item(category_name, item_title):
    """Edit a item."""
    if "username" not in login_session:
        return redirect("/login")
    editedItem = session.query(Item).filter_by(id = item_id).one()
    if request.method == "POST":
        if request.form["name"]:
            editedItem.name = request.form["name"].strip()
        if request.form["description"]:
            editedItem.description = request.form["description"].strip()
        if request.form["price"]:
            editedItem.price = request.form["price"].strip()
        if request.form["course"]:
            editedItem.course = request.form["course"].strip()
        session.add(editedItem)
        session.commit()
        flash("Item Item '%s' Successfully Edited" % editedItem.name)
        return redirect(url_for("showItem", category_id = category_id))
    else:
        return render_template("editItem.html", 
            title = "Edit a item", category_id = category_id, item_id = item_id, item = editedItem)

# Delete a item.
@app.route("/catalog/<path:category_name>/<path:item_title>/delete", methods = ["GET", "POST"])
def delete_item(category_name, item_title):
    """Delete a item."""
    if "username" not in login_session:
        return redirect("/login")
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if request.method == "POST":
        session.delete(itemToDelete)
        session.commit()
        flash("Item Item '%s' Successfully Deleted" % itemToDelete.name)
        return redirect(url_for("showItem", category_id = category_id))
    else:
        return render_template("deleteItem.html", 
            title = "Delete a item", category_id = category_id, item_id = item_id, item = itemToDelete)


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host = "0.0.0.0", port = 5000)