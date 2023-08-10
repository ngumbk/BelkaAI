import numpy as np
import pandas as pd
import re


def prepare_data():
    apartments_data = pd.read_csv('raw_apartments_data.csv', encoding='cp1251')

    # Дропаем точно ненужные колонки
    apartments_data = apartments_data.drop(['photo', 'phone', 'email'], axis=1)

    # Преобразуем дату в месяц
    apartments_data['date'] = apartments_data['date'].apply(
        lambda x: int(x[3:5]))
    apartments_data = apartments_data.rename(columns={'date': 'date_month'})

    # Оставляем в поле type только кол-во комнат в квартире
    # И переименовываем в rooms. Как выяснилось, при разделении признака type
    # На 2 новых, во втором признаке около 70% пропусков. Не будем его сохранять
    apartments_data['type'] = apartments_data['type'].apply(
        lambda x: x.split(' ')[0] if isinstance(x, str) else x)
    apartments_data = apartments_data.rename(columns={'type': 'rooms'})
    # Т.к. кол-во квартир с неопределенным кол-вом комнат небольшое, зададим их
    # Вручную, ориентируясь по описанию
    rooms_dic = {
        9: 'Студия',
        41: 'Дроп',
        66: 'Двухкомнатная',
        73: 'Дроп',
        112: 'Студия',
        228: 'Однокомнатная',
        275: 'Трехкомнатная',
        290: 'Двухкомнатная',
        332: 'Дроп',
        374: 'Двухкомнатная',
        396: 'Дроп',
        406: 'Дроп',
        423: 'Дроп',
        457: 'Студия',
        495: 'Дроп',
        501: 'Дроп'
    }
    # Применяем словарь и удаляем лишние строки
    for i, v in rooms_dic.items():
        apartments_data.loc[i, 'rooms'] = v
    drop_rows = apartments_data[apartments_data['rooms'] == 'Дроп'].index
    apartments_data = apartments_data.drop(drop_rows)
    apartments_data = apartments_data.reset_index(drop=True)
    # Применяем Label Encoding
    apartments_data['rooms'] = apartments_data['rooms'].replace(
        {'Студия': 0,
         'Однокомнатная': 1,
         'Двухкомнатная': 2,
         'Трехкомнатная': 3,
         'Четырехкомнатная': 4})
    
    # Убираем номер дома для каждого адреса
    apartments_data['address'] = apartments_data['address'].apply(
        lambda x: ' '.join(x.split(' ')[:-1]) if isinstance(x, str) else x)
    # Хотя для большинства адресов предыдущая функция сработала,
    # Некоторые адреса выбивались из общего формата и были неверно обработаны
    # Восстановим эти адреса
    address_dic = {
        23: 'Карла Маркса',
        25: 'Им. газеты "Правда"',
        80: 'Ленина пр-т',
        81: 'Ленина пр-т',
        83: 'Торфяная',
        112: 'Карла Маркса',
        121: 'Им. газеты "Правда"',
        140: 'Горнолыжная',
        162: 'Карла Маркса',
        177: 'Ленина пр-т',
        183: 'Дроп',
        185: 'Труда',
        267: 'Им. газеты "Правда"',
        302: 'Подольская',
        378: 'Дроп',
        384: 'Дроп',
        388: 'Набережная',
        433: 'Дроп',
        475: 'Дроп',
        489: 'Ленина пр-т',
        509: 'Ленина пр-т'
    }
    # Применяем словарь и удаляем лишние строки
    for i, v in address_dic.items():
        apartments_data.loc[i, 'address'] = v

    drop_rows = apartments_data[apartments_data['address'] == 'Дроп'].index
    apartments_data = apartments_data.drop(drop_rows)
    apartments_data = apartments_data.reset_index(drop=True)
    # Удаляем из названий улиц 'ул.'
    apartments_data['address'] = apartments_data['address'].apply(
        lambda x: re.sub(r'ул\.?\s?', '', x))


    print(apartments_data.head(3))


if __name__ == '__main__':
    prepare_data()
