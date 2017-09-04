#!/usr/bin/env python3
#
# Item model for Catalog App.
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from category import Category
from user import User


class Item(Base):
    __tablename__ = "item"
    __table_args__ = (UniqueConstraint('category_id', 'title', name='key'),)

    id = Column(Integer, primary_key=True)
    title = Column(String(80), nullable=False)
    description = Column(String(250))
    created_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, default=datetime.utcnow,
                          onupdate=datetime.utcnow)
    category_id = Column(Integer, ForeignKey("category.id"))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    @classmethod
    def update(self):
        self.updated_date = datetime.utcnow()

    def __repr__(self):
        return ("<Item: id={:d}, title='{}', created_date={}, last_updated={},"
                " category_id={:d}, user_id={:d}>".format(
                    self.id, self.title, self.created_date, self.updated_date,
                    self.category_id, self.user_id))

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
