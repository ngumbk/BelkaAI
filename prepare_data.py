import numpy as np
import pandas as pd
import re


def set_street_category(street):
    if street == 'Ленина пр-т':
        return 'Lenina'
    elif street == 'Карла Маркса':
        return 'Marksa'
    else:
        return 'another'
    

# Учитывая относительно небольшую разницу между ценами на квартиры в левобрежных
# Районах, при кодировании их можно объединить
def set_district_category(district):
    if district == 'Ленинский':
        return 'Leninskiy'
    elif district == 'Орджоникидзевский':
        return 'Ordzhonikidzevskiy'
    elif district == 'Правобережный':
        return 'Pravoberezhniy'
    else:
        return 'Levoberezhniy'


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
    # Выделим 3 категории улиц: "Ленина пр-т", "Карла Маркса" и все остальные
    # Применим для этих категорий One-Hot Encoding
    apartments_data['street_cat'] = apartments_data['address'].apply(
        set_street_category)
    streets_encoded = pd.get_dummies(
        apartments_data['street_cat'], prefix='street')
    apartments_data = pd.concat([apartments_data, streets_encoded], axis=1)
    # Удаляем ненужные поля
    apartments_data = apartments_data.drop(['street_cat'], axis=1)

    # Очистка района
    # Создадим и применим словарь для унификации названий районов
    district_dic = {'ленинский': 'Ленинский',
                'Правобережный район': 'Правобережный',
                'правобережный': 'Правобережный',
                'Правоббережный': 'Правобережный',
                'П/б': 'Правобережный',
                'орджоникидзевский': 'Орджоникидзевский',
                'Орджонекидзевский': 'Орджоникидзевский',
                'Ленинский (Левый берег)': 'Ленинский (левый берег)'}
    apartments_data = apartments_data.replace({'district': district_dic})

    district_missed_df = apartments_data[
        apartments_data['district'].isna()].copy()

    # При поиске комментариев с упоминание левого берега не нашлось
    # Ни одного подходящего района, поэтому л/б не включен в замену
    district_patterns = {'Орджоникидзевский': r'[Оо]рдж',
                        'Ленинский': '[Лл]енинск',
                        'Правобережный': '/[Пп]равобб?ер'}

    for district, pattern in district_patterns.items():
        indices = []
        for index, row in district_missed_df.iterrows():
            if isinstance(row['comment'], str):
                match = re.search(pattern, row['comment'])
                if match:
                    apartments_data.loc[index, 'district'] = district
                    indices.append(index)
    # Этот цикл помог понизить процент пропусков района с 35% до 28.4%. Причем
    # Качество восстановления довольно высокое, хотя использовался только regexp

    # Сопоставление улиц районам
    # Эти адреса были проверены по heatmap, т.к. не были присвоены никакому
    # Району Магнитогорска
    addresses_to_drop = ['Анджиевского', 'Болотная', 'Габдрауфа Давлетова',
                         'Горнолыжная', 'Курортная', 'Молодежная', 'Новая',
                         'Привокзальная', 'Псекупская', 'Российская', 'Садовая',
                         'Солнечный Берег', 'Степная', 'Тагира Кусимова',
                         'Торфяная', 'Центральная', 'Черемушки', 'Школьная']

    drop_rows = apartments_data[
        apartments_data['address'].isin(addresses_to_drop)].index
    apartments_data = apartments_data.drop(drop_rows)
    apartments_data = apartments_data.reset_index(drop=True)

    # Составим датафрейм с сопоставлением района каждой улице, чтобы заполнить
    # Этими значениями пропуски
    df_address_district = apartments_data.groupby('address')['district'].apply(
        lambda x: x.mode()).reset_index()
    
    # Отбираем только районы-дубликаты, для которых было несколько мод
    # Считаем наиболее популярный район из пары мод, чтобы присвоить его
    df_address_district_duplicates = df_address_district[
        df_address_district.duplicated('address', keep=False)].copy()
    df_address_district_duplicates['district_popularity'] = df_address_district_duplicates['district'].map(
        lambda x: len(apartments_data[apartments_data['district'] == x]))
    
    # Оставляем экземпляры дубликатов с наиболее популярным районом

    # Считаем максимальное кол-во вхождений в датасете для районов,
    # Сопоставленных дублирующимся улицам
    max_popular_districts = df_address_district_duplicates.groupby('address')[
        'district_popularity'].max()

    # Добавляем столбец с максимальным кол-вом вхождений района для данной улицы
    df_address_district_duplicates = df_address_district_duplicates.merge(
        max_popular_districts, left_on='address', right_index=True, 
        suffixes=('', '_max'))

    # Оставляем те строки, для которых кол-во вхождений является максимальным
    df_address_district_duplicates = df_address_district_duplicates[
        df_address_district_duplicates['district_popularity'] == df_address_district_duplicates['district_popularity_max']]

    # Удаляем лишние столбцы
    df_address_district_duplicates = df_address_district_duplicates.drop(
        ['district_popularity', 'district_popularity_max'], axis=1)
    # Удаляем дубликаты из исходного датафрейма с улицами/районами
    mask = df_address_district.duplicated('address', keep=False)
    df_address_district = df_address_district[~mask]

    # Добавляем исправленные дубликаты в исходный датафрейм
    df_address_district = pd.concat(
        [df_address_district, df_address_district_duplicates], axis=0)

    # Удаляем лишнюю колонку и обновляем индексы
    df_address_district = df_address_district.drop('level_1', axis=1)
    df_address_district = df_address_district.reset_index(drop=True)

    # Формируем словарь, с сопоставлением моды района каждой улице
    mode_district_by_address = {}
    for row in df_address_district.values:
        mode_district_by_address[row[0]] = row[1]

    # Добавляем районы вручную
    mode_district_by_address['Зеленая'] = 'Правобережный'
    mode_district_by_address['Лермонтова'] = 'Орджоникидзевский (левый берег)'
    mode_district_by_address['Оранжерейная'] = 'Правобережный'
    mode_district_by_address['Писарева'] = 'Ленинский'
    mode_district_by_address['уральская'] = 'Ленинский'

    # Применяем словарь
    apartments_data['district'] = apartments_data.apply(
        lambda row: mode_district_by_address.get(row['address']) if
        pd.isna(row['district']) else row['district'], axis=1)

    # Создаем новые поля
    apartments_data['district_cat'] = apartments_data['district'].apply(
        set_district_category)
    districts_encoded = pd.get_dummies(apartments_data['district_cat'],
                                       prefix='district')
    apartments_data = pd.concat([apartments_data, districts_encoded], axis=1)

    # Удаляем лишние поля
    apartments_data = apartments_data.drop(
        ['address', 'comment', 'district', 'district_cat'], axis=1)
    
    # Формируем 2 новых признака посредством разделения признака 'floor'
    apartments_data['apaertment_floor'] = apartments_data['floor'].apply(lambda x: x.split('/')[0])
    apartments_data['house_floors'] = apartments_data['floor'].apply(lambda x: x.split('/')[1])
    apartments_data = apartments_data.drop('floor', axis=1)
    apartments_data.head()

    print(apartments_data.head(3))


if __name__ == '__main__':
    prepare_data()
