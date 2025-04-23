import base64
import sys
from os.path import dirname, abspath
from typing import List
from urllib.parse import urljoin
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

sys.path.insert(0, dirname(dirname(abspath(__file__))))

from settings import settings


def get_info(category: str, N: int = 3) -> List[dict]:
    '''
    Функция получения информации о промте по категории
    :param category: (str) - Название категории
    :param N: (int) - Количество промтов из топа
    :return: (dict) - Информация о популярных промтах в формате
    '''
    url = settings.URL
    MAIN_URL = settings.URL



    # Настраиваем драйвер
    driver = webdriver.Chrome()
    driver.set_window_size(1920, 1080)
    driver.get(url)

    # Ищем кнопку Categories и нажимаем
    сategories = driver.find_element(By.XPATH, '/html/body/app-root/app-home/site-nav/nav/div/ul[1]/li[2]/a')
    сategories.click()

    # Получаем HTML после нажатия с категориями
    updated_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-home/site-nav/nav/div[2]"))
    )
    inner_html = updated_element.get_attribute('innerHTML')
    soup = BeautifulSoup(inner_html, 'lxml')

    # Создаем словарь категорий
    categories_dict = {}

    # Находим все элементы меню
    nav_items = soup.find_all('li', class_='second-nav-item')

    for item in nav_items:
        link = item.find('a', class_='nav-link')
        if link:
            category_name = link.find('span').get_text(strip=True)
            category_link = link['href']
            categories_dict[category_name] = category_link

    for key, value in categories_dict.items():
        categories_dict[key] = MAIN_URL + value

    print(list(categories_dict.keys()))

    # Получаем ссылку на нужную нам категорию
    url = categories_dict[category]

    # Словарь с трендовыми промтами
    trending_prompts = dict()

    # Получаем страницу с промтами и загружаем в словарь первые 20 трендовых промтов
    driver.get(url)
    updated_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/app-root/app-category/div[1]/div[2]/item-top-list/div"))
    )
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", updated_element)
    inner_html = updated_element.get_attribute('innerHTML')
    soup = BeautifulSoup(inner_html, 'lxml')

    for prom in soup.find_all('a', attrs={"_ngcontent-ng-c2927900627": ""}):
        trending_prompts[prom.get('title')] = MAIN_URL + prom.get('href')

    # Кнопка перелистования промтов
    nav_link = driver.find_element(By.CSS_SELECTOR, "item-top-list div.page-next")

    # Заполняем словарь до тех пор, пока не будет нужное количество промтов
    while len(trending_prompts) < N:
        nav_link.click()
        updated_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "/html/body/app-root/app-category/div[1]/div[2]/item-top-list/div"))
        )
        inner_html = updated_element.get_attribute('innerHTML')
        soup = BeautifulSoup(inner_html, 'lxml')

        for prom in soup.find_all('a', attrs={"_ngcontent-ng-c2927900627": ""}):
            trending_prompts[prom.get('title')] = MAIN_URL + prom.get('href')

    # Итоговый список с информациями о промтах
    result = list()

    # Прогоняем каждый промт и получаем информацию о нём
    for key, value in list(trending_prompts.items())[:N]:
        driver.get(value)

        # Получение описания
        try:
            description = driver.find_element(By.CSS_SELECTOR, "div.description expandable-text div")
            description = BeautifulSoup(description.get_attribute('innerHTML'), 'lxml').find('div', class_='content')
            description = description.get_text(strip=False)
        except Exception as s:
            print(s)
            description = None

        # Получение цена
        try:
            price = driver.find_element(By.CSS_SELECTOR, "span.price")
            price = BeautifulSoup(price.get_attribute('innerHTML'), 'lxml')
            price = price.get_text(strip=False)
        except Exception as s:
            print(s)
            price = None

        # Получение статистики
        try:
            statistics = dict()
            star = driver.find_element(By.CSS_SELECTOR, "div.stats-and-icon item-stats")
            star = BeautifulSoup(star.get_attribute('innerHTML'), 'lxml')
            stats = star.find_all('div', class_='item-stat')
            for stat in stats:
                # Извлекаем информацию из item-stat-top
                top_value = stat.find('div', class_='item-stat-top').find('span').get_text(strip=True)

                # Извлекаем информацию из из item-stat-bottom
                bottom_name = stat.find('div', class_='item-stat-bottom').get_text(strip=True)
                statistics[bottom_name] = top_value
        except Exception as s:
            print(s)
            statistics = None

        # Получение превью в формате bytes64
        try:
            preview = driver.find_element(By.CSS_SELECTOR, "preview-images")
            preview = BeautifulSoup(preview.get_attribute('innerHTML'), 'lxml')
            preview = preview.find('img')
            preview = urljoin(url, preview['src'])
            preview = requests.get(preview).content
            preview = base64.b64encode(preview).decode('utf-8')
        except Exception as s:
            print(s)
            preview = None

        title = key

        info = {
            'title': title,
            'description': description,
            'price': price,
            'statistics': statistics,
            'preview': preview
        }

        # Добавления промта в итоговый список
        result.append(info)

    return result
