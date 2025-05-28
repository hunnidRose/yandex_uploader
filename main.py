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
if breed.lower() in all_breeds_list['message']:
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

# Создаем папку на Яндекс.Диске
params = {
    'path': breed.capitalize()
}
headers['Content-Type'] = 'application/json'
response = requests.put(yandex_base_url + '/v1/disk/resources',
                        params=params, headers=headers)

# Получаем список из названий файлов, находящихся в папке,
# чтобы в дальнейшем избежать загрузки одинаковых изображений
params = {
    'path': f'{breed.capitalize()}/'
}
del headers['Content-Type']
response = requests.get(yandex_base_url + '/v1/disk/resources',
                        params=params, headers=headers)
folder_items = response.json()['_embedded']['items']
folder_file_names = []
for item in folder_items:
    folder_file_names.append(item['name'])

# Загружаем случайное изображение породы в созданную папку
headers['Content-Type'] = 'application/json'
dog_base_url = f'https://dog.ceo/api/breed/{breed.lower()}/'
if all_breeds_list['message'][breed.lower()]:
    for sub_breed in all_breeds_list['message'][breed.lower()]:
        response = requests.get(f'{dog_base_url}{sub_breed}/images/random')
        image_url = response.json()['message']
        image_name = f'{sub_breed}_{breed.lower()}_{image_url.split('/')[-1]}'
        params = {
            'path': f'{breed.capitalize()}/{image_name}',
            'url': image_url
        }
        if image_name not in folder_file_names:
            requests.post(yandex_base_url + '/v1/disk/resources/upload',
                            params=params, headers=headers)
else:
    response = requests.get(f'{dog_base_url}images/random')
    image_url = response.json()['message']
    image_name = f'{breed.lower()}_{image_url.split('/')[-1]}'
    params = {
        'path': f'{breed.capitalize()}/{image_name}',
        'url': image_url
    }
    requests.post(yandex_base_url + '/v1/disk/resources/upload',
                  params=params, headers=headers)
