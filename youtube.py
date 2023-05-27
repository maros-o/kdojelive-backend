from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import db

load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY')
YT = build('youtube', 'v3', developerKey=API_KEY)

youtube_streams = []


def get_channel_info(channel_id):
    request = YT.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()

    return response["items"][0]["snippet"]


def get_channel_streams(channel_id):
    request = YT.search().list(
        part="snippet",
        channelId=channel_id,
        eventType="live",
        type="video"
    )
    response = request.execute()

    streams = response["items"]

    if len(streams) == 0:
        return []

    stream_info = []

    for stream in streams:
        video_id = stream["id"]["videoId"]
        video_request = YT.videos().list(
            part="liveStreamingDetails",
            id=video_id
        )
        video_response = video_request.execute()
        live_streaming_details = video_response["items"][0]["liveStreamingDetails"]
        viewer_count = live_streaming_details["concurrentViewers"]

        stream_info.append({
            "title": stream["snippet"]["title"],
            "viewer_count": viewer_count,
            "thumbnail": stream["snippet"]["thumbnails"]["medium"]["url"],
            'stream_url': f'https://youtube.com/watch?v={video_id}'
        })

    return stream_info


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
