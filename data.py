#!/usr/bin/env python3
#
# Reporting tool that prints out reports (in plain text) based on the
# data in the database.
from models.user import User
from models.category import Category
from models.item import Item
from database import session, create_db
from random import randint
import utils.lorem_ipsum_generator as lig

print("data.py start...")

# Create database.
create_db()

# Create dummy users.
USERS = [("Alain Boisvert", "ay.boisvert@gmail.com"),
         ("Mathieu Boisvert", "boisvert.my@gmail.com"),
         ("Frederic Boisvert", "fredric.boisvert@gmail.com"),
         ("Marie-Claude Guertin", "mc.guertin@gmail.com")]

users = []
for item in USERS:
    user = User(name=item[0], email=item[1], picture=None)
    session.add(user)
    session.commit()
    users.append(user)
    print(user)


def random_user():
    pos = randint(0, len(users) - 1)
    return users[pos]


# Category and items of that category.
category1 = Category(name="Local Business or Place", user=random_user())
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
    item = Item(title=value,
                description=lig.random_para(250),
                category=category1,
                user=random_user())
    session.add(item)
    session.commit()
    print(item)

# Category and items of that category.
category2 = Category(name="Company, Organisation or Institution",
                     user=random_user())
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
    item = Item(title=value,
                description=lig.random_para(250),
                category=category2,
                user=random_user())
    session.add(item)
    session.commit()
    print(item)

# Category and items of that category.
category3 = Category(name="Brand or Product", user=random_user())
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
    item = Item(title=value,
                description=lig.random_para(250),
                category=category3,
                user=random_user())
    session.add(item)
    session.commit()
    print(item)

# Category and items of that category.
category4 = Category(name="Artist, Band or Public Figure", user=random_user())
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
    item = Item(title=value,
                description=lig.random_para(250),
                category=category4,
                user=random_user())
    session.add(item)
    session.commit()
    print(item)

# Category and items of that category.
category5 = Category(name="Entertainment", user=random_user())
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
    item = Item(title=value,
                description=lig.random_para(250),
                category=category5,
                user=random_user())
    session.add(item)
    session.commit()
    print(item)

# Category and items of that category.
category6 = Category(name="Cause or Community", user=random_user())
session.add(category6)
session.commit()
print(category6)

print("data.py finish!")
