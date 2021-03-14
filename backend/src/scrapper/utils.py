import pandas as pd
from backend.src.db import car_data as car_table, engine
import traceback


def save_data(data_to_save, should_delete_previous_data=False):
    with engine.connect() as connection:
        transaction = connection.begin()
        try:
            if should_delete_previous_data:
                connection.execute(car_table.delete())
            data_to_save.to_sql('car_data', connection, if_exists='append', index=False)
            transaction.commit()
        except:
            traceback.print_exc()
            transaction.rollback()


def save_new_data_without_duplicates(new_data, source):
    source_old_data = pd.read_sql(car_table.select().where(car_table.c.source == source), engine)
    other_source_old_data = pd.read_sql(car_table.select().where(car_table.c.source != source), engine)
    old_data = pd.concat([source_old_data, other_source_old_data])

    for enum_col in ['transmission', 'fuel', 'origin']:
        old_data[enum_col] = old_data[enum_col].apply(lambda x: x.name)

    all_data = pd.concat([old_data, new_data])
    all_data = all_data.drop_duplicates(subset=['id'])
    save_data(all_data)
