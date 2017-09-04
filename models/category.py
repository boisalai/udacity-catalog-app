#!/usr/bin/env python3
#
# Category model for Catalog App.
from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from database import Base
from user import User


class Category(Base):
    __tablename__ = "category"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_date = Column(DateTime, default=datetime.utcnow,
                          onupdate=datetime.utcnow, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User)

    def update(self):
        self.updated_date = datetime.utcnow()

    def __repr__(self):
        return ("<Category: id={:d}, name='{}', created_date={}, "
                "last_updated={}, user_id={:d}>".format(
                    self.id, self.name, self.created_date,
                    self.updated_date, self.user_id))

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
