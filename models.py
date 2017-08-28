#!/usr/bin/env python3
#
# SQLAlchemy models for Catalog App.
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship


print("models.py start...")

DATABASE_NAME = "catalog.db"

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False)
    email = Column(String(80), nullable = False, unique = True)
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

# TODO: One-to-Many Relationships.
class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key = True)
    name = Column(String(80), nullable = False, index = True)
    created_date = Column(DateTime, default = datetime.utcnow, nullable = False)
    updated_date = Column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow, nullable = False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    def update(self):
        self.updated_date = datetime.utcnow()

    def __repr__(self):
        return ("<Category: id={:d}, name='{}', created_date={}, "
                "last_updated={}, user_id={:d}>".format(self.id, self.name, 
                self.created_date, self.updated_date, self.user_id))

    # Add a property decorator to serialize information from this database.
    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            "id": self.id,
            "name": self.name,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "user_id": self.user_id
        }

class Item(Base):
    __tablename__ = "item"
    __table_args__ = (UniqueConstraint('category_id', 'title', name = 'key'),)

    id = Column(Integer, primary_key = True)
    title = Column(String(80), nullable = False)
    description = Column(String(250))
    created_date = Column(DateTime, default = datetime.utcnow)
    updated_date = Column(DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @classmethod
    def update(self):
        self.updated_date = datetime.utcnow()

    def __repr__(self):
        return ("<Item: id={:d}, title='{}', created_date={}, last_updated={},"
                " category_id={:d}, user_id={:d}>".format(self.id, self.title, 
                self.created_date, self.updated_date, self.category_id, 
                self.user_id))

    # Add a property decorator to serialize information from this database.
    @property
    def serialize(self):
        """Return object data in easily serializeable format."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_date": self.created_date,
            "updated_date": self.updated_date,
            "category_id": self.category_id,
            "user_id": self.user_id
        }

engine = create_engine("sqlite:///catalog.db")
Base.metadata.create_all(engine)

print("models.py finish!")