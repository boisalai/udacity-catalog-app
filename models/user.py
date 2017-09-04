#!/usr/bin/env python3
#
# User model for Catalog App.
from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(80), nullable=False, unique=True)
    picture = Column(String(250))

    def __init__(self, name, email, picture):
        self.name = name
        self.email = email
        self.picture = picture

    def __repr__(self):
        return ("<User: id={:d}, name='{}', email='{}', picture='{}'>".format(
                self.id, self.name, self.email, self.picture))

    # Add a property decorator to serialize information from this database.
    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "picture": self.picture
        }
