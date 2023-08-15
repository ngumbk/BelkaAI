from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from catboost import CatBoostRegressor
import joblib


class RegRequest(BaseModel):
    #date_month: int
    rooms_number: int
    square_all: float
    #square_living: float
    #square_kitchen: float
    street_Lenina: bool
    street_Marksa: bool
    street_another: bool
    district_Leninskiy: bool
    district_Levoberezhniy: bool
    district_Ordzhonikidzevskiy: bool
    district_Pravoberezhniy: bool
    apartment_floor: int
    house_floors: int
    agency_AN_Klyuchi: bool
    agency_Individual: bool
    agency_RioLuks: bool
    agency_another: bool
    square_l2o: float
    # price: int


price_model = CatBoostRegressor()
price_model.load_model('catboost_model567.cbm')
app = FastAPI()


@app.get('/')
async def get_root():
    return {'Hello': 'World!'}


@app.get('/predict_apartment_price/')
async def predict_apartment_price(input_data: RegRequest):
    input_data = dict(input_data)
    input_features = list(input_data.values())
    input_features = np.array(input_features).reshape(-1, 1)
    scaler = MinMaxScaler()
    input_features = scaler.fit_transform(input_features).reshape(1, -1)
    prediction = price_model.predict(input_features)
    return {'Predicted price': prediction[0]}
