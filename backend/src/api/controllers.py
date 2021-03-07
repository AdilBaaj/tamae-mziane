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
        if model:
            query = query.filter_by(model=model)
        data = query.all()
        df = pd.DataFrame(data)
        df['transmission'] = df['transmission'].apply(lambda x: x.name)
        df['fuel'] = df['fuel'].apply(lambda x: x.name)
        df['origin'] = df['origin'].apply(lambda x: x.name)
        df = df.drop(['scrapping_date'], axis=1)
        return df.to_dict('records')


api.add_resource(CarsData, '/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
