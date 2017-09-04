#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
from models.user import User
from database import session


def create_user(login_session):
    """Create a new user from login session and return his id."""
    newUser = User(name=login_session["username"],
                   email=login_session["email"],
                   picture=login_session["picture"])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session["email"]).one_or_none()
    return user.id


def get_user_info(user_id):
    """Return user object from his id."""
    user = session.query(User).filter_by(id=user_id).one_or_none()
    return user


def get_user_id(email):
    """Return user id from his email."""
    try:
        user = session.query(User).filter_by(email=email).one_or_none()
        return user.id
    except:
        return None
