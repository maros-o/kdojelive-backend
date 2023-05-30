import requests
import time

trovo_streams = []
MAX_DELAY = 60 * 15


def get_all_streams():
    url = 'https://raw.githubusercontent.com/maros-o/kdojelive-trovo/main/streams.json'
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return []

    if response.status_code != 200:
        return []

    if data['last_updated'] < time.time() - MAX_DELAY:
        return []

    return data['streams']


def update_trovo_streams():
    global trovo_streams
    start = time.time()
    print(' updating trovo streams..')
    trovo_streams = get_all_streams()
    print(f' trovo streams updated in {round(time.time() - start, 3)} secs')


def get_streams():
    global trovo_streams
    return trovo_streams
