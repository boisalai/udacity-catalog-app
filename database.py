#!/usr/bin/env python3
#
# Database.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Connect to database and create database session.
engine = create_engine("sqlite:///catalog.db")
Base = declarative_base()
DBSession = sessionmaker(bind=engine)
session = DBSession()


def create_db():
    Base.metadata.create_all(engine)
