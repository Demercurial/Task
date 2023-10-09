import requests
import pandas as pd
from datetime import datetime as dt


MAIN_COLUMNS = ['id','name','year','countries','rating_kp','rating_imdb']
HEADERS = {'X-API-KEY' : TOKEN} # TOKEN необходимо получить у бота @kinopoiskdev
BASE_URL = 'https://api.kinopoisk.dev/v1.3/movie?page={}&limit={}&rating.kp={}'

def create_dataframe(resp_json:dict)-> pd.DataFrame:
# формирование структуры датафрейм 
    main_data = []
    for elem_docs in resp_json['docs']:
        temp_data_str = [elem_docs['id'], elem_docs['name'], elem_docs['year'], ','.join(x['name'] for x in elem_docs['countries']),
                        elem_docs['rating']['kp'],elem_docs['rating']['imdb']]
        main_data.append(temp_data_str)
    return pd.DataFrame(columns=MAIN_COLUMNS, data=main_data)

def parse_url(url:str,headers:str)-> dict:
# проверка доступа
    resp = requests.get(url,headers=headers)
    if resp.status_code == 200:
        return resp
    else:
        raise Exception('Код:',resp.status_code,'- Не пошло дело')
    
def create_response(rating:str, page_number = 1, limit = 10):
# формирование json
    url = BASE_URL.format(page_number, limit, rating)
    resp_json = parse_url(url, HEADERS).json()
    return resp_json

def main_load_data(rating:str)-> pd.DataFrame:
# формирование основного датафрейма 
    base_response = create_response(rating)
    total_pages = base_response['pages']
    result_df = create_dataframe(base_response)
    arr = [result_df]
    for page in range(2, total_pages+1):
        response_tmp = create_response(rating=rating, page_number=page)
        df_tmp = create_dataframe(response_tmp)
        arr.append(df_tmp)
    return pd.concat(arr)


def mean_kp_imbd(df: pd.DataFrame)-> float:
# среднее расхождение оценки от платформы IMBD и Кинопоиск 
    return round((abs(df['rating_kp'].sum() - df['rating_imdb'].sum())/len(df)),2)


def successful_year(df: pd.DataFrame)-> int:
# Самый успешный год кинопроизводства с точки зрения оценок
    df_year = df.groupby('year').agg(['sum','count'])
    dict_year_sum = dict(df_year['rating_kp']['sum'])
    dict_year_count = dict(df_year['rating_kp']['count'])
    for key in dict_year_sum.keys():
        dict_year_count[key] = dict_year_sum[key] / dict_year_count[key]
    target_grade = max(dict_year_count.values())
    return [key for key, value in dict_year_count.items() if value == target_grade]  


def succesful_countries(df: pd.DataFrame)-> str:
# Самая успешная страна с точки зрения оценок 
    arr = []
    for ind, row in df.iterrows():
        result = zip(row['countries'].split(','), [row['rating_kp']]* len(row['countries'].split(',')))
        res_dict = dict(result)
        for key, val in res_dict.items():
            df_tmp = pd.DataFrame(data={'countries': [key], 'value': [val]})
            arr.append(df_tmp)
    df_countries = pd.concat(arr)
    df_succesful_countries = df_countries.groupby('countries').agg(['sum','count'])
    df_succesful_countries_sum = dict(df_succesful_countries['value']['sum'])
    df_succesful_countries_count = dict(df_succesful_countries['value']['count'])
    for key in df_succesful_countries_sum.keys():
        df_succesful_countries_count[key] = df_succesful_countries_sum[key] / df_succesful_countries_count[key]
    target_grade = max(df_succesful_countries_count.values())
    return [key for key, value in df_succesful_countries_count.items() if value == target_grade]

def raw_data_load(df: pd.DataFrame):
# загрузка датафрейма в папку raw_data
    file_date = dt.strftime(dt.now(), '%Y%m%d')
    file_name = f'kp_{file_date}.csv'
    df.to_csv(f'raw_data/{file_name}')

df = main_load_data('5.1-5.2') # указан короткий диапазон значений (для тз использовать'6-8')
raw_data_load(df)

print('Самая успешная страна с точки зрения оценок -',succesful_countries(df))
print('Среднее расхождение оценки от платформы IMBD и Кинопоиск -',mean_kp_imbd(df)) 
print('Самый успешный год кинопроизводства с точки зрения оценок -',*successful_year(df))
