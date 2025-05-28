import datetime
import json
import logging
import requests

# Получаем список всех существующих пород
all_breeds_url = 'https://dog.ceo/api/breeds/list/all'
response = requests.get(all_breeds_url)
all_breeds_list = response.json()

# Путем пользовательского ввода получаем название породы
# и делаем проверку на наличие ее в нашем списке
breed = input('Название породы(на англ.): ')
breed_lower = breed.lower()
if breed_lower in all_breeds_list['message']:
    print('Порода успешно найдена', end='\n\n')
else:
    raise KeyError(f"Порода '{breed}' не найдена")

# Основной URL для запросов к Яндекс.Диску
yandex_base_url = 'https://cloud-api.yandex.net'

# Получаем токен пользователя и делаем пробный запрос
key = input('Токен с Полигона Яндекс.Диска: ')
headers = {
    'Accept': 'application/json',
    'Authorization': f'OAuth {key}'
}
response = requests.get(yandex_base_url + '/v1/disk', headers=headers)
status_code = response.status_code
if status_code == 200:
    print('Подключение установлено', end='\n\n')
else:
    raise ConnectionError(response.json()['message'])
