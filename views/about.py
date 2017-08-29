#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from flask import Blueprint, render_template

about_blueprint = Blueprint('about', __name__)


@about_blueprint.route("/catalog/about")
def about():
    """Show about page."""
    return render_template("about.html")
