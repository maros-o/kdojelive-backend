from dotenv import load_dotenv
import googleapiclient.discovery
import os
import db
import time
import requests
import re
import json

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


def get_video_info(video_id):
    request = YT.videos().list(
        part="snippet,liveStreamingDetails",
        id=video_id
    )
    response = request.execute()

    return response["items"][0]


def insert_channel(channel_id):
    channel_info = get_channel_info(channel_id)
    channel_name = channel_info["snippet"]["title"]
    channel_thumbnail = channel_info["snippet"]["thumbnails"]["medium"]["url"]

    db.insert_youtube_channels([(channel_id, channel_name, channel_thumbnail)])


def get_streams_all():
    new_streams = []
    channels = db.get_youtube_channels()

    for channel in channels:
        channel_id = channel[0]

        print(f'checking channel: {channel[1]}')

        stream_video_id = get_livestream_id(channel_id)
        if stream_video_id is None:
            continue

        channel_name = channel[1]
        channel_thumbnail = channel[2]
        stream_info = get_video_info(stream_video_id)

        stream_title = stream_info["snippet"]["title"]
        stream_thumbnail = stream_info["snippet"]["thumbnails"]["medium"]["url"]

        live_streaming_details = stream_info['liveStreamingDetails']

        if "concurrentViewers" in live_streaming_details:
            stream_viewer_count = int(
                live_streaming_details["concurrentViewers"])
        else:
            stream_viewer_count = 0

        clean_stream = {
            'user_name': channel_name,
            'title': stream_title,
            'viewer_count': stream_viewer_count,
            'stream_thumbnail_url': stream_thumbnail,
            'platform': 'youtube',
            'category': None,
            'stream_url': f'https://www.youtube.com/watch?v={stream_video_id}',
            'user_thumbnail_url': channel_thumbnail,
        }

        new_streams.append(clean_stream)

    return new_streams


def get_livestream_id(channel_id):
    try:
        url = f'https://youtube.com/channel/{channel_id}/live/?hl=en&noapp=1'
        response = session.get(url, cookies={
            'CONSENT': f'YES+cb.20210328-17-p0.en-GB+FX+{int(time.time())}'
        }).text

        href_url_match = re.search(
            r'rel="canonical" href="(.*?)"', response)

        if href_url_match:
            href_url = href_url_match.group(1)

            if href_url.startswith('https://www.youtube.com/channel/'):
                return None

            if 'publishDate":{"simpleText":"Scheduled' in response:
                return None

            return href_url.split('=')[1]

        return None

    except requests.RequestException as e:
        print(f'Error occurred during the request: {str(e)}')
        return None


def update_youtube_streams():
    global youtube_streams
    youtube_streams = get_streams_all()


def get_streams():
    update_youtube_streams()
    return youtube_streams

# TODO: add update to current streams every 5 minutes with just yt api


# start = time.time()

# # print(get_livestream_id('UCLqMHRtQA10qPQtG8qKCp_w'))
# # streams = get_video_info(get_livestream_id('UCp48ChS_trJdlvkbwACxXNA'))

# streams = get_streams_all()

# with open('results/youtube.json', 'w') as f:
#     f.write(json.dumps(streams))

# print(f"{round(time.time() - start, 3)} seconds")
