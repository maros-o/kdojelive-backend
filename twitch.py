import requests
import db
import os
import threading
from dotenv import load_dotenv
import time
import json

load_dotenv()

UPDATE_TIME = 120.0
CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
OAUTH_TOKEN = os.getenv('TWITCH_OAUTH_TOKEN')
LANGUAGE_CODES = {
    'cs': 60,
    'sk': 20,
}
STREAM_THUMBNAIL_SIZE = (320, 180)
HEADERS = {
    'Client-ID': CLIENT_ID,
    'Authorization': f'Bearer {OAUTH_TOKEN}'
}


def request_data(url):
    response = requests.get(url, headers=HEADERS)
    data = response.json()['data']

    return data


def get_user_thumbnail_url(user_id):
    url = f'https://api.twitch.tv/helix/users?id={user_id}'
    data = request_data(url)
    user_thumbnail_url = data[0]['profile_image_url']

    return user_thumbnail_url


def set_user_thumbnails():
    user_thumbnails = {}
    raw_thumbnails = db.get_twitch_user_thumbnails()

    for thumbnail in raw_thumbnails:
        user_thumbnails[thumbnail[0]] = thumbnail[1]

    return user_thumbnails


twitch_streams = []
user_thumbnails = set_user_thumbnails()


def get_all_streams():
    raw_streams = []
    new_streams = []

    for language_code in LANGUAGE_CODES.items():
        url = f'https://api.twitch.tv/helix/streams?language={language_code[0]}&first={language_code[1]}'
        raw_streams += request_data(url)

    db_insert_values = []

    for raw_stream in raw_streams:
        clean_stream = {
            'user_name': raw_stream['user_name'],
            'title': raw_stream['title'],
            'viewer_count': raw_stream['viewer_count'],
            'stream_thumbnail_url': raw_stream['thumbnail_url'].replace('{width}', str(STREAM_THUMBNAIL_SIZE[0])).replace('{height}', str(STREAM_THUMBNAIL_SIZE[1])),
            'platform': 'twitch',
            'category': raw_stream['game_name'],
            'stream_url': f'https://twitch.tv/{raw_stream["user_name"]}'
        }

        if clean_stream['user_name'] not in user_thumbnails:
            user_thumbnail_url = get_user_thumbnail_url(raw_stream['user_id'])

            user_thumbnails[raw_stream['user_name']] = user_thumbnail_url
            db_insert_values.append(
                (raw_stream['user_name'], user_thumbnail_url))

        clean_stream['user_thumbnail_url'] = user_thumbnails[raw_stream['user_name']]

        new_streams.append(clean_stream)

    if len(db_insert_values) > 0:
        db.insert_twitch_user_thumbnails(db_insert_values)

    return new_streams


def update_twitch_streams():
    global twitch_streams
    start = time.time()
    print(' updating twitch streams..')
    twitch_streams = get_all_streams()
    print(f' twitch streams updated in {round(time.time() - start, 3)} secs')


def get_streams():
    global twitch_streams
    return twitch_streams
