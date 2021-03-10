import pandas as pd
from backend.src.db import car_data as car_table, engine
import traceback


def save_new_data(new_data, source):
    source_old_data = pd.read_sql(car_table.select().where(car_table.c.source == source), engine)
    other_source_old_data = pd.read_sql(car_table.select().where(car_table.c.source != source), engine)
    old_data = pd.concat([source_old_data, other_source_old_data])

    for enum_col in ['transmission', 'fuel', 'origin']:
        old_data[enum_col] = old_data[enum_col].apply(lambda x: x.name)

    all_data = pd.concat([old_data, new_data])
    all_data = all_data.drop_duplicates(subset=['id'])

    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            connection.execute(car_table.delete())
            all_data.to_sql('car_data', connection, if_exists='append', index=False)
            transaction.commit()
        except:
            traceback.print_exc()
            transaction.rollback()
