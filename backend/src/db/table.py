from sqlalchemy import *
from backend.src.db.enum_classes import Transmission, Fuel, Origin
from backend.src.db import engine

metadata = MetaData()

car_data = Table(
    'car_data',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('price', Integer, nullable=False),
    Column('brand', String, nullable=False),
    Column('model', String, nullable=False),
    Column('transmission', Enum(Transmission), nullable=False),
    Column('fuel', Enum(Fuel), nullable=False),
    Column('carrosserie', String),
    Column('finish', String),
    Column('mileage', Integer, nullable=False),
    Column('tax_rating', Integer),
    Column('horse_power', Integer),
    Column('city', String),
    Column('origin', Enum(Origin)),
    Column('date_on_the_road', String),
    Column('year', Integer),
    Column('vignette_price', Integer),
    Column('url', String),
    Column('source', String),
    Column('scrapping_date', DateTime)
)

if __name__ == '__main__':
    metadata.create_all(engine)
