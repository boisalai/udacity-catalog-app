#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from flask import Blueprint, flash, make_response, request, redirect
from flask import render_template, url_for
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import views.user as user
import httplib2
import json
import requests
import random
import string


auth = Blueprint('auth', __name__)

GOOGLE_CLIENT_SECRET = "client_secret.json"
GOOGLE_CLIENT_ID = json.loads(
    open(GOOGLE_CLIENT_SECRET, "r").read())["web"]["client_id"]


@auth.route("/login")
def show_login():
    """Create anti-forgery state token."""
    state = "".join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session["state"] = state
    return render_template("login.html", STATE=state)


@auth.route("/gconnect", methods=["POST"])
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
    user_id = user.get_user_id(data["email"])
    if not user_id:
        user_id = user.create_user(login_session)
    login_session["user_id"] = user_id

    output = "<h1>Welcome, "
    output += login_session["username"]
    output += "!</h1>"
    output += '<img src="' + login_session["picture"] + '" '
    output += 'style = "width: 300px; height: 300px; border-radius: 150px; '
    output += '-webkit-border-radius: 150px; -moz-border-radius: 150px;"> '
    flash(
        "You are now logged in as {}.".format(login_session["username"]),
        "success")
    return output


@auth.route("/gdisconnect")
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


@auth.route("/fbconnect", methods=["POST"])
def fbconnect():
    """Facebook connect."""
    if request.args.get("state") != login_session["state"]:
        response = make_response(json.dumps("Invalid state parameter."), 401)
        response.headers["Content-Type"] = "application/json"
        return response

    # Access token received (see access_token).
    access_token = request.data

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
    user_id = user.get_user_id(login_session["email"])
    if not user_id:
        user_id = user.create_user(login_session)
    login_session["user_id"] = user_id

    output = "<h1>Welcome, "
    output += login_session["username"]

    output += "!</h1>"
    output += '<img src="'
    output += login_session["picture"]
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;'
    output += ' -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as {}.".format(login_session["username"]), "success")
    return output


@auth.route("/fbdisconnect")
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


@auth.route("/disconnect")
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
        flash("You have successfully been logged out.", "success")
        return redirect(url_for("category.show_categories"))
    else:
        flash("You were not logged in.", "success")
        return redirect(url_for("category.show_categories"))


def delete_key_login_session(key):
    try:
        del login_session[key]
    except:
        return
