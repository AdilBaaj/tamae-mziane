from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql+psycopg2://tamane:mziane@database:5432/cars')

# https://docs.sqlalchemy.org/en/13/orm/session_basics.html
# create a configured "Session" class
Session = sessionmaker(bind=engine)
