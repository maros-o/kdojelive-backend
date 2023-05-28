from dotenv import load_dotenv
import googleapiclient.discovery
import os
import db
import time
import requests
import re
import json
from bs4 import BeautifulSoup

load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY_1')
YT = googleapiclient.discovery.build('youtube', 'v3', developerKey=API_KEY)

youtube_streams = []
session = requests.Session()


def get_channel_info(channel_id):
    request = YT.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()

    return response["items"][0]


def get_channel_activity(channel_id):
    request = YT.activities().list(
        part="snippet",
        channelId=channel_id
    )
    response = request.execute()

    return response["items"]


def get_video_info(video_id):
    request = YT.videos().list(
        part="snippet,liveStreamingDetails",
        id=video_id
    )
    response = request.execute()

    return response["items"][0]


def get_channel_streams(channel_id):
    return []
    # url = f"https://www.googleapis.com/youtube/v3/search?key={API_KEY}&channelId={channel_id}&part=snippet,id&eventType=live&type=video"
    # response = requests.get(url).json()

    # streams = response["items"]

    # if len(streams) == 0:
    #     return []

    # stream_info = []

    # for stream in streams:
    #     video_id = stream["id"]["videoId"]

    #     video = get_video_info(video_id)

    #     live_streaming_details = video["liveStreamingDetails"]
    #     viewer_count = live_streaming_details["concurrentViewers"]

    #     stream_info.append({
    #         "title": stream["snippet"]["title"],
    #         "viewer_count": viewer_count,
    #         "thumbnail": stream["snippet"]["thumbnails"]["medium"]["url"],
    #         'stream_url': f'https://youtube.com/watch?v={video_id}'
    #     })

    # return stream_info


def insert_channel(channel_id):
    channel_info = get_channel_info(channel_id)
    channel_name = channel_info["title"]
    channel_thumbnail = channel_info["thumbnails"]["medium"]["url"]

    db.insert_youtube_channels([(channel_id, channel_name, channel_thumbnail)])


def get_streams_all():
    new_streams = []

    channels = db.get_youtube_channels()

    for channel in channels:
        channel_id = channel[0]
        channel_name = channel[1]
        channel_thumbnail = channel[2]

        streams = get_channel_streams(channel_id)

        for stream in streams:
            stream_title = stream["title"]
            stream_thumbnail = stream["thumbnail"]
            stream_viewer_count = stream["viewer_count"]

            clean_stream = {
                'user_name': channel_name,
                'title': stream_title,
                'viewer_count': stream_viewer_count,
                'stream_thumbnail_url': stream_thumbnail,
                'platform': 'youtube',
                'category': None,
                'user_thumbnail_url': channel_thumbnail,
                'stream_url': stream["stream_url"]
            }

            new_streams.append(clean_stream)

    return new_streams


def update_youtube_streams():
    global youtube_streams
    youtube_streams = get_streams_all()


def get_streams():
    update_youtube_streams()
    return youtube_streams


# def get_live(channel_id):
#     response = requests.get(
#         f'https://youtube.com/channel/{channel_id}/live/', cookies={'CONSENT': 'YES+cb.20210328-17-p0.en-GB+FX+{}'.format(int(time.time()))})

#     # get href of <link rel="canonical" href="https://www.youtube.com/watch?v=uD0X6gvrisc" />

#     tree = HTMLParser(response.text)
#     stream = {}

#     for link in tree.css('link'):
#         if link.attributes.get('rel') == 'canonical':
#             href_url = link.attributes.get('href')

#             if href_url.startswith('https://www.youtube.com/channel/'):
#                 return None

#             stream['stream_url'] = href_url

#     title_match = re.search(
#         r'videoDetails":{"playerOverlayVideoDetailsRenderer":{"title":{"simpleText":"(.*?)"}', response.text)
#     if title_match:
#         stream['title'] = title_match.group(1)

#     viewer_count_match = re.search(
#         r'Právě sleduje: "},{"text":"(.*?)"}', response.text)
#     if viewer_count_match:
#         stream['viewer_count'] = viewer_count_match.group(1)

#     print(response.text)
#     print(stream)

#     return response.text


def get_livestream_id(channel_id):
    response = session.get(f'https://youtube.com/channel/{channel_id}/live/?hl=en', cookies={
        'CONSENT': 'YES+cb.20210328-17-p0.en-GB+FX+{}'.format(int(time.time()))
    })
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.content, 'lxml')
    link = soup.find('link', rel='canonical')

    if not link:
        return None

    href_url = link.get('href')
    if href_url.startswith('https://www.youtube.com/channel/'):
        return None

    scheduled_match = re.search(
        r'publishDate":{"simpleText":"Scheduled', response.text)

    if scheduled_match:
        return None

    return href_url.split('=')[1]


start = time.time()

for i in range(100):
    print(get_livestream_id('UCLqMHRtQA10qPQtG8qKCp_w'))
    print(get_livestream_id('UCp48ChS_trJdlvkbwACxXNA'))

print(f"{round(time.time() - start, 3)} seconds")
