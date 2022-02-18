import os
from bs4 import BeautifulSoup as bs
import requests
import re
from urllib import request
import zipfile

DRIVER_FOLDER = r'd:\_tmp\ucd'
SITE_URL = 'https://chromedriver.chromium.org/downloads'
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), 'download')

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
        print('Тут будет exc')
    return driver_ver


def get_new_drivers_list(url: str, driver_ver: list) -> list:
    '''
    Парсим сайт с загрузками выбираем ссылки на страницу загрузки
    :param url: URL
    :return: список с сайтами для загрузки
    '''
    url_list = []
    page = requests.get(url)
    soup = bs(page.text, features='html.parser')
    search_string = 'chromedriver.storage.googleapis.com'
    for data in soup.find_all(href=True):
        link = data['href']
        # Выбираем только ссылки с загрузкой и убираем note.txt
        if search_string in link and 'notes.txt' not in link:
            ver_url = link.split('=')[-1].split('.')[0]
            if ver_url not in driver_ver:
                url_list.append(link)
    return url_list


def download_drivers(url_list):
    driver_dict = {}
    driver_name = r'chromedriver_win32.zip'
    #Формируем словарь версия драйвер:адресс для скачивания
    for url in url_list:
        #Получаем версию из url
        version = url.split('path=')[1].split('.')[0]
        url = url.replace('index.html?path=', '')
        driver_dict.update({version:url+driver_name})
    #Сохраняем фаил
    for ver, url in driver_dict.items():
        tmp_file_name = ver+ '_'+ url.split('/')[-1]
        zip_file_name = os.path.join(DOWNLOAD_FOLDER, tmp_file_name)
        request.urlretrieve(url, zip_file_name)

def uzip_rename_move(src_folder, dst_folder):
    for file in os.listdir(src_folder):
        if file.endswith('.zip'):
            ver = file.split('_')[0]
            driver_name = 'chromedriver' + ver + '.exe'
            full_path = os.path.join(src_folder, file)
            with zipfile.ZipFile(full_path, 'r') as zf:
                zf.extractall(DOWNLOAD_FOLDER)
            os.remove(full_path)
            for file_exe in os.listdir(src_folder):
                if file_exe.endswith('exe'):
                    os.rename(os.path.join(src_folder, file_exe), os.path.join(dst_folder, driver_name))

if __name__ == '__main__':
    driver_ver_list = get_current_drivers(DRIVER_FOLDER)
    url_list = get_new_drivers_list(SITE_URL, driver_ver_list)
    download_drivers(url_list)
    uzip_rename_move(DOWNLOAD_FOLDER, DRIVER_FOLDER)