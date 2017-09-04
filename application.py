#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
#
# This application provides a list of items within a variety of categories
# as well as provide a user registration and authentication system.
# Registered users will have the ability to post, edit and delete their own
# items. This web app is a project for the Udacity FSWDN
from flask import Flask
from views.about import about_blueprint
from views.category import category
from views.item import item
from views.auth import auth
from views.api import api

app = Flask(__name__)

# Register all the blueprints.
app.register_blueprint(about_blueprint)
app.register_blueprint(category)
app.register_blueprint(item)
app.register_blueprint(auth)
app.register_blueprint(api)


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.run(host="0.0.0.0", port=8000, debug=True)
