from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
import db

load_dotenv()

API_KEY = os.getenv('YOUTUBE_API_KEY')
YT = build('youtube', 'v3', developerKey=API_KEY)


youtube_streams = []
# youtube_channels = db.get_youtube_channels()


def get_channel_info(channel_id):
    request = YT.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_id
    )
    response = request.execute()

    return response["items"][0]["snippet"]


def is_channel_czech_or_slovak(channel_id):
    channel_info = get_channel_info(channel_id)
    country = channel_info["country"]

    return country == "CZ" or country == "SK"


def is_channel_live(channel_id):
    request = YT.search().list(
        part="snippet",
        channelId=channel_id,
        eventType="live",
        type="video"
    )
    response = request.execute()

    print(response)

    return len(response["items"]) > 0


CHANNEL_ID = "UCROnsopSryzM2WaxxeNICOA"

print(is_channel_live(CHANNEL_ID))
print(is_channel_czech_or_slovak(CHANNEL_ID))


def get_streams():
    return youtube_streams
