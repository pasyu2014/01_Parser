

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os

def get_links(url):
    '''
    Отправляет GET-запрос на указанный URL.
    Парсит страницу с помощью BeautifulSoup для поиска всех тегов <a>.
    Собирает уникальные ссылки, которые ведут на другие сайты.
    '''
    try:
        response = requests.get(url, timeout=5)  # Установим таймаут
        response.raise_for_status()  # Проверяем на ошибки
    except requests.Timeout:
        print(f"Таймаут при запросе {url}. Пропускаем.")
        return set()  # Возвращаем пустое множество вместо списка
    except requests.RequestException as e:
        print(f"Ошибка при запросе {url}: {e}")
        return set()

    soup = BeautifulSoup(response.text, 'html.parser')
    links = set()

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # Превращаем относительные ссылки в абсолютные
        full_url = urljoin(url, href)
        # Проверяем, что ссылка ведет на другой сайт
        if urlparse(full_url).netloc != urlparse(url).netloc:
            links.add(full_url)

    return links

def parse_links(start_url, depth, output_file=None):
    '''
    Использует множество для отслеживания посещённых ссылок и очередь для обработки ссылок, которые нужно посетить.
    Повторяет процесс для каждой полученной ссылки до заданной глубины.
    '''
    if depth == 0:
        print(f"Глубина парсинга равна 0. Возвращаем только начальный URL: {start_url}")
        return {start_url}

    visited = set()
    to_visit = {start_url}
    current_depth = 0

    while to_visit and current_depth < depth:
        current_url = to_visit.pop()
        if current_url in visited:
            continue

        print(f"Обрабатываем: {current_url}")
        visited.add(current_url)

        links = get_links(current_url)
        to_visit.update(links - visited)  # Обновляем список ссылок для посещения

        if output_file:
            # Проверка существования файла
            if os.path.exists(output_file):
                print(f"Файл {output_file} существует. Новые результаты будут добавлены.")
            else:
                print(f"Создаем новый файл: {output_file}")

            with open(output_file, 'a') as f:
                for link in links:
                    f.write(link + '\n')

        current_depth += 1

    return visited

if __name__ == "__main__":  # Правильная проверка имени модуля
    start_url = input("Введите URL для парсинга: ")
    depth = int(input("Введите глубину парсинга (0 - только главная ссылка): "))
    output_choice = input("Выводить в терминал (T) или сохранять в файл (F)? ").strip().upper()

    output_file = None
    if output_choice == 'F':
        output_file = input("Введите имя файла для сохранения результата: ")

    visited_links = parse_links(start_url, depth, output_file)

    if output_choice == 'T':
        print("\nПолученные ссылки:")
        for link in visited_links:
            print(link)
