import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import time


def parse_page(url, df):
    if len(df) > 0:
        time.sleep(10)
    page = requests.get(url)
    page.encoding = page.apparent_encoding
    soup = BeautifulSoup(page.text, 'html.parser')
    
    all_tables = soup.find_all('table')
    table = all_tables[20]
    
    apartments = []

    for row in table.findAll('tr'):
        cells = row.findAll('td')
        if len(cells) == 14:
            apartment = []
            for cell in cells:
                apartment.append(cell.text.strip())
            apartments.append(apartment)
    
    new_df = pd.DataFrame(apartments)
        
    return pd.concat([df, new_df], ignore_index=True)


def main():
    # Ссылка на базовую страницу с продажей квартир на citystar.ru
    url_base = 'http://citystar.ru/detal.htm?d=43&nm=%CE%E1%FA%FF%E2%EB%E5%ED%E8%FF+%2D+%CF%F0%EE%E4%E0%EC+%EA%E2%E0%F0%F2%E8%F0%F3+%E2+%E3%2E+%CC%E0%E3%ED%E8%F2%EE%E3%EE%F0%F1%EA%E5&pN='
    urls = [url_base + str(i) for i in range(1, 7)]
    index = ['photo', 'published', 'type', 'district', 'adress', 'floor', 'square_all',
         'square_living', 'square_kitchen', 'comment', 'price (thousand rubles)',
         'phone', 'agency', 'email']
    rename_dic = {i:k for i, k in enumerate(index)}
    
    apartments_data = pd.DataFrame()
    for url in urls:
        apartments_data = parse_page(url, apartments_data)
        print(f'Обработано {len(apartments_data)} квартир')

    # Обработка сырых данных
    apartments_data = apartments_data.rename(columns=rename_dic)
    apartments_data = apartments_data.replace('', np.nan)
    apartments_data = apartments_data.drop(['photo', 'phone', 'email'], axis=1)
    apartments_data['comment'] = apartments_data['comment'].apply(
        lambda x: re.sub(r'\r\n{1,6}', ' ', x) if isinstance(x, str) else x)
    
    # Сохранение данных в формате csv
    apartments_data.to_csv('apartments_data.csv', encoding='cp1251',
                           index=False)


if __name__ == '__main__':
    main()
    