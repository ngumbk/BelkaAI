import requests


req_dic = {
    #'date_month': 8,
    'rooms_number': 2,
    'square_all': 68.5,
    #'square_living': 45.0,
    #'square_kitchen': 15.0,
    'street_Lenina': False,
    'street_Marksa': False,
    'street_another': True,
    'district_Leninskiy': True,
    'district_Levoberezhniy': False,
    'district_Ordzhonikidzevskiy': False,
    'district_Pravoberezhniy': False,
    'apartment_floor': 1,
    'house_floors': 2,
    'agency_AN_Klyuchi': False,
    'agency_Individual': True,
    'agency_RioLuks': False,
    'agency_another': False,
    'square_l2o': 0.458333,
    #'price': 3000
}

result = requests.get('http://127.0.0.1:8000/')

print(result.text)

result = requests.get('http://127.0.0.1:8000/predict_apartment_price/',
                      json=req_dic)

print(result.text)