from backend.src.db import Session, car_data as car_table
from flask import Flask
from flask_restful import Resource, Api, reqparse
import pandas as pd

app = Flask(__name__)
api = Api(app)


class CarsData(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('brand')
        parser.add_argument('model')
        args = parser.parse_args()
        brand = args.get('brand')
        model = args.get('model')
        session = Session()
        query = session.query(car_table).filter_by(brand=brand)
        session.close()
        if model:
            query = query.filter_by(model=model)
        data = query.all()
        df = pd.DataFrame(data)
        df['transmission'] = df['transmission'].apply(lambda x: x.name)
        df['fuel'] = df['fuel'].apply(lambda x: x.name)
        df['origin'] = df['origin'].apply(lambda x: x.name)
        df = df.drop(['scrapping_date'], axis=1)
        return df.to_dict('records')


class Brands(Resource):
    def get(self):
        session = Session()
        brands = session.query(car_table.c.brand).distinct(car_table.c.brand).all()
        session.close()
        return [b[0] for b in brands]


class Models(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('brand')
        args = parser.parse_args()
        brand = args.get('brand')
        if not brand:
            return 'Specify a brand', 400
        session = Session()
        models = session.query(car_table.c.model).distinct(car_table.c.model).filter(car_table.c.brand == brand).all()
        session.close()
        return [m[0] for m in models]


class Stats(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('brand')
        parser.add_argument('model')
        args = parser.parse_args()
        brand = args.get('brand')
        model = args.get('model')
        if not brand or not model:
            return 'Specify a brand and a model', 400
        session = Session()
        data = session.query(car_table).filter_by(brand=brand).filter_by(model=model).all()
        session.close()
        if data:
            df = pd.DataFrame(data)
            stats_df = df[['price', 'year']].groupby('year').price.agg(['mean', 'min', 'max'])
            return stats_df.to_dict('index')
        return {}


api.add_resource(CarsData, '/api/car-data')
api.add_resource(Brands, '/api/brands')
api.add_resource(Models, '/api/models')
api.add_resource(Stats, '/api/stats')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
