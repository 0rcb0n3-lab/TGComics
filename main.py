import os
import random
import requests
import shutil

from dotenv import load_dotenv
from urllib.parse import urlparse


def fetch_total_comics_count():
    url = 'https://xkcd.com/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    comics_metadata = response.json()
    return comics_metadata['num']


def fetch_comic_details(comic_number):
    url = f'https://xkcd.com/{comic_number}/info.0.json'
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def save_image(image_url, image_path):
    response = requests.get(image_url)
    response.raise_for_status()
    with open(image_path, 'wb') as file:
        file.write(response.content)


def send_photo_to_telegram(bot_token, chat_id, image_path, caption_text):
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    with open(image_path, 'rb') as image:
        response = requests.post(
            url,
            data={
                'chat_id': chat_id,
                'caption': caption_text,
            },
            files={
                'photo': image,
            },
        )
    response.raise_for_status()


def delete_temp_folder(path):
    if os.path.exists(path):
        shutil.rmtree(path)


def main():
    load_dotenv()

    tg_token = os.environ['TGBOT_TOKEN']
    tg_chat_id = os.environ['TG_CHAT_ID']

    temp_folder = 'comics'
    os.makedirs(temp_folder, exist_ok=True)

    try:
        print("Получаем общее количество комиксов.")
        total_comics_count = fetch_total_comics_count()

        random_comic_id = random.randint(1, total_comics_count)
        print(f"Выбираем случайный комикс №{random_comic_id}.")
        comic_details = fetch_comic_details(random_comic_id)

        target_image_url = comic_details['img']
        comic_description = comic_details.get('alt', '')

        # получаем расширение файла из URL (.png, .jpg, .gif)
        parsed_url = urlparse(target_image_url)
        _, file_extension = os.path.splitext(parsed_url.path)
        local_image_path = os.path.join(temp_folder, f'{random_comic_id}{file_extension}')

        print("Скачиваем и сохраняем изображение.")
        save_image(target_image_url, local_image_path)

        print("Публикуем в Telegram.")
        send_photo_to_telegram(tg_token, tg_chat_id, local_image_path, comic_description)
        print("Успешно опубликовано!")

    finally:
        print("Удаляем временные файлы и папку.")
        delete_temp_folder(temp_folder)


if __name__ == '__main__':
    main()
