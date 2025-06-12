import datetime
import json
import logging
import os
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Получаем текущие дату и время для именования файлов в папке info
current_time = datetime.datetime.now()
year = current_time.year
month = current_time.month
day = current_time.day
hour = current_time.hour
minute = current_time.minute
second = current_time.second
time_for_name = f'{year}_{month:02}_{day:02}_{hour:02}_{minute:02}_{second:02}'

# Получаем расположение папки info
current_path = os.getcwd()
info_path = os.path.join(current_path, 'info', f'info_{time_for_name}.json')

# Список для добавления в него информации по загруженным
# файлам и преобразования его в json-файл
info_list = []

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
sub_breeds_list = all_breeds_list['message'][breed.lower()]
if sub_breeds_list:
    counter = 0
    logging.info('Загружаю изображения на Диск...')
    for idx, sub_breed in enumerate(sub_breeds_list, 1):
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
            counter += 1
            logging.info(f'[{idx}/{len(sub_breeds_list)}] '
                         f'{image_name}[Статус: Успешно загружено]')
            info_list.append({'file_name': image_name})
        else:
            logging.warning(f'[{idx}/{len(sub_breeds_list)}] '
                            f'{image_name}[Статус: Отменено]'
                            f'[Причина: Данное изображение уже на Диске]')
    logging.info(f'Успешно загружено '
                 f'{counter}/{len(sub_breeds_list)} изображений')
else:
    logging.info('Загружаю изображение на Диск...')
    response = requests.get(f'{dog_base_url}images/random')
    image_url = response.json()['message']
    image_name = f'{breed.lower()}_{image_url.split('/')[-1]}'
    params = {
        'path': f'{breed.capitalize()}/{image_name}',
        'url': image_url
    }
    if image_name not in folder_file_names:
        requests.post(yandex_base_url + '/v1/disk/resources/upload',
                      params=params, headers=headers)
        logging.info(f'{image_name}[Статус: Успешно загружено]')
        info_list.append({'file_name': image_name})
    else:
        logging.warning(f'{image_name}[Статус: Отменено]'
                        f'[Причина: Данное изображение уже на Диске]')

# Создаем json-файл в папке info
file_name = f'info_{time_for_name}.json'
logging.info('Создаю json с информацией по загрузке...')
if info_list:
    with open(info_path, 'w', encoding='utf-8') as file:
        json.dump(info_list, file, ensure_ascii=False, indent=2)
    logging.info(f'{file_name}[Статус: Создан]')
else:
    logging.warning(f'{file_name}[Статус: Отменен]'
                    f'[Причина: Отсутствуют данные для записи]')
