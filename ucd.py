import os
from bs4 import BeautifulSoup as bs
import requests
import re
from urllib import request
import zipfile
import sys
import configparser
import ast
import logging
import logging.config

SITE_URL = 'https://chromedriver.chromium.org/downloads'
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')

def get_logger():
    # Логер
    logging.config.fileConfig(os.path.join(os.getcwd(), 'logger.ini'), disable_existing_loggers = False)
    logger = logging.getLogger('plogger')
    return logger
logger = get_logger()

def get_config(config_path: str, section: str) -> dict:
    """
    Получаем конфиг
    :param config_path: путь до файла конфигурации
    :param section: имя секции
    :return: возвращает словарь из options указанной секции
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    logger.info('Фаил конфигурации прочитан')
    return dict(config.items(section))


def get_current_drivers(folder: str) -> list:
    '''
    Ищет файлы драйвера в указанной директории
    :param folder: Путь к директории с драйверами
    :return: версий драйверов
    '''
    driver_ver = []
    re_dig = re.compile(r"\d+")
    if os.path.exists(DRIVER_FOLDER):
        for file in os.listdir(DRIVER_FOLDER):
            if file.startswith('chromedriver'):
                ver = re.search(re_dig, file)
                if ver:
                    driver_ver.append(ver.group(0))
    else:
        logger.error('Каталога с драйверами не существует')
    return driver_ver


def get_new_drivers_list(url: str, driver_ver: list) -> list:
    '''
    Парсим сайт с загрузками выбираем ссылки на страницу загрузки
    :param url: URL
    :return: список с сайтами для загрузки
    '''
    logger.info('get_new_drivers_list запустился')
    url_list = []
    try:
        page = requests.get(url)
    except Exception as e:
        logger.exception('Ошибка подключения к сайту')
        sys.exit(1)
    soup = bs(page.text, features='html.parser')
    search_string = 'chromedriver.storage.googleapis.com'
    for data in soup.find_all(href=True):
        link = data['href']
        # Выбираем только ссылки с загрузкой и убираем note.txt
        if search_string in link and 'notes.txt' not in link:
            # Берем версию драйвера из URL
            ver_url = link.split('=')[-1].split('.')[0]
            if ver_url not in driver_ver:
                url_list.append(link)
    logger.info('get_new_drivers_list выполнился')
    return url_list


def download_drivers(url_list, download_folder):
    '''
    Загрузка драйверов
    :param url_list:
    :return:
    '''
    logger.info('download_drivers запустился')
    driver_dict = {}
    driver_name = r'chromedriver_win32.zip'
    # Формируем словарь версия драйвер:адресс для скачивания
    for url in url_list:
        # Получаем версию из url
        version = url.split('path=')[1].split('.')[0]
        url = url.replace('index.html?path=', '')
        driver_dict.update({version: url + driver_name})
    # Сохраняем фаил
    for ver, url in driver_dict.items():
        tmp_file_name = ver + '_' + url.split('/')[-1]
        #Задаем имя файла и катало гля загрузки в формате ver_...
        if not os.path.exists(download_folder):
            os.makedirs(download_folder)
        zip_file_name = os.path.join(download_folder, tmp_file_name)
        try:
            request.urlretrieve(url, zip_file_name)
        except Exception as e:
            logger.exception('Ошибка загрузки драйверов')
    logger.info('download_drivers завершил работу')
def uzip_rename_move(src_folder, dst_folder):
    '''
    Распаковывает архив, и переименовывает фаил с перемещением
    :param src_folder: Директория для загрузки
    :param dst_folder: Директория куда складывать драйвера
    :return:
    '''
    logger.info('uzip_rename_move запустился')
    #Проверяем файлы в каталоге загрузки, ищем .zip
    for file in os.listdir(src_folder):
        if file.endswith('.zip'):
            #Получаем версию
            ver = file.split('_')[0]
            #Формируем имя файла и полный путь
            driver_name = 'chromedriver' + ver + '.exe'
            full_path = os.path.join(src_folder, file)
            with zipfile.ZipFile(full_path, 'r') as zf:
                zf.extractall(DOWNLOAD_FOLDER)
            os.remove(full_path)
            for file_exe in os.listdir(src_folder):
                if file_exe.endswith('exe'):
                    try:
                        os.rename(os.path.join(src_folder, file_exe), os.path.join(dst_folder, driver_name))
                    except Exception as e:
                        logger.exception('Ошибка перемещения файлов')
    logger.info('uzip_rename_move завершил работу')
if __name__ == '__main__':
    logger.info('Скрипт начал работу')
    config = get_config(os.path.join(os.getcwd(), 'setting.ini'), 'FOLDER')
    DRIVER_FOLDER = config['driver_folder']
    driver_ver_list = get_current_drivers(DRIVER_FOLDER)
    url_list = get_new_drivers_list(SITE_URL, driver_ver_list)
    if url_list:
        download_drivers(url_list, DOWNLOAD_FOLDER)
        uzip_rename_move(DOWNLOAD_FOLDER, DRIVER_FOLDER)
        logger.info('Драйверы обновлены')
    else:
        logger.info('Обновлений драйверов не было')
