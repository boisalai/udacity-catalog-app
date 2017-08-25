#!/usr/bin/env python3
#
# Reporting tool that prints out reports (in plain text) based on the
# data in the database.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Category, Item


print("data.py start...")

DATABASE_NAME = "catalog.db"
engine = create_engine("sqlite:///" + DATABASE_NAME)

# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)

# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy users.
user1 = User(name = "Alain Boisvert", 
             email = "ay.boisvert@gmail.com", 
             picture = "http://xyw.png")
session.add(user1)
session.commit()
print(user1)

# https://www.eukhost.com/blog/webhosting/how-to-set-up-a-facebook-business-page-a-complete-guide/
# Category and items of that category.
category1 = Category(name = "Local Business or Place", user = user1)
session.add(category1)
session.commit()
print(category1)

values = ["Airport", 
          "Arts/Entertainment/Nightlife", 
          "Attractions/Things to Do", 
          "Bank/Financial Services",
          "Bar",
          "Bookshop",
          "Business Services",
          "Church/Religious Organisation",
          "Cinema",
          "Club",
          "Community/Government",
          "Concert Venue",
          "DIY",
          "Doctor",
          "Event Planning/Event Services",
          "Food/Groceries",
          "Health/Medical/Pharmacy",
          "Hospital/Clinic",
          "Hotel",
          "Landmark",
          "Lawyer",
          "Library",
          "Local Business",
          "Middle School",
          "Museum/Art Gallery",
          "Outdoor Gear/Sporting Goods",
          "Pet Services",
          "Professional Services",
          "Property",
          "Public Places",
          "Restaurant/Cafe",
          "School",
          "Shopping/Retail",
          "Spas/Beauty/Personal Care",
          "Sports Venue",
          "Sports/Recreation/Activities",
          "Tours/Sightseeing",
          "Transport",
          "University",
          "Vehicles"]

for value in values:
  item = Item(title = value,
              description = "XYZ", 
              category = category1,
              user = user1)
  session.add(item)
  session.commit()
  print(item)

# Category and items of that category.
category2 = Category(name = "Company, Organisation or Institution", user = user1)
session.add(category2)
session.commit()
print(category2)

values = ["Aerospace/Defence",
          "Bank/Financial Institution",
          "Biotechnology",
          "Cars and Parts",
          "Cause",
          "Chemicals",
          "Church/Religious Organisation",
          "Community Organisation",
          "Company",
          "Computers/Technology",
          "Consulting/Business Services",
          "Education",
          "Energy/Utility",
          "Engineering/Construction",
          "Farming/Agriculture",
          "Food/Beverages",
          "Government Organisation",
          "Health/Beauty",
          "Health/Medical/Pharmaceuticals",
          "Industrials",
          "Insurance Company",
          "Internet/Software",
          "Legal/Law",
          "Media/News/Publishing",
          "Middle School",
          "Mining/Materials",
          "Non-governmental Organisation (NGO)",
          "Non-profit Organisation",
          "Organisation",
          "Political Organisation",
          "Political Party",
          "Preschool",
          "Primary School",
          "Retail and Consumer Merchandise",
          "School",
          "Small Business",
          "Telecommunication",
          "Transport/Freight",
          "Travel/Leisure",
          "University"]

for value in values:
  item = Item(title = value,
              description = "XYZ", 
              category = category2,
              user = user1)
  session.add(item)
  session.commit()
  print(item)

# Category and items of that category.
category3 = Category(name = "Brand or Product", user = user1)
session.add(category3)
session.commit()
print(category3)

values = ["App Page",
          "Appliances",
          "Baby Goods/Kids Goods",
          "Bags/Luggage",
          "Board Game",
          "Building Materials",
          "Camera/Photo",
          "Cars",
          "Clothing",
          "Commercial Equipment",
          "Computers",
          "Electronics",
          "Food/Beverages",
          "Furniture",
          "Games/Toys",
          "Health/Beauty",
          "Home Decor",
          "Household Supplies",
          "Jewellery/Watches",
          "Kitchen/Cooking",
          "Medications",
          "Office Supplies",
          "Patio/Garden",
          "Pet Supplies",
          "Phone/Tablet",
          "Product/Service",
          "Software",
          "Tools/Equipment",
          "Video Game",
          "Vitamins/Supplements",
          "Website",
          "Wine/Spirits"]

for value in values:
  item = Item(title = value,
              description = "XYZ", 
              category = category3,
              user = user1)
  session.add(item)
  session.commit()
  print(item)

# Category and items of that category.
category4 = Category(name = "Artist, Band or Public Figure", user = user1)
session.add(category4)
session.commit()
print(category4)

values = ["Actor/Director",
          "Artist",
          "Author",
          "Blogger",
          "Business Person",
          "Chef",
          "Coach",
          "Comedian",
          "Dancer",
          "Designer",
          "Entertainer",
          "Entrepreneur",
          "Fictional Character",
          "Film Character",
          "Government Official",
          "Journalist",
          "Musician/Band",
          "News Personality",
          "Pet",
          "Photographer",
          "Politician",
          "Producer",
          "Public Figure",
          "Scientist",
          "Sportsperson",
          "Teacher",
          "Writer"]

for value in values:
  item = Item(title = value,
              description = "XYZ", 
              category = category4,
              user = user1)
  session.add(item)
  session.commit()
  print(item)

# Category and items of that category.
category5 = Category(name = "Entertainment", user = user1)
session.add(category5)
session.commit()
print(category5)

values = ["Album",
          "Amateur Sports Team",
          "Book",
          "Book Series",
          "Bookshop",
          "Cinema",
          "Concert Tour",
          "Concert Venue",
          "Fictional Character",
          "Film",
          "Film Character",
          "Library",
          "Magazine",
          "Movie Studio",
          "Music Award",
          "Music Chart",
          "Music Video",
          "Performance Art",
          "Radio Station",
          "Record Label",
          "School Sports Team",
          "Song",
          "Sports League",
          "Sports Team",
          "Sports Venue",
          "Theatrical Play",
          "TV Channel",
          "TV Network",
          "TV Programme",
          "TV/Film Award"]

for value in values:
  item = Item(title = value,
              description = "XYZ", 
              category = category5,
              user = user1)
  session.add(item)
  session.commit()
  print(item)

# Category and items of that category.
category6 = Category(name = "Cause or Community", user = user1)
session.add(category6)
session.commit()
print(category6)

print("data.py finish!")
