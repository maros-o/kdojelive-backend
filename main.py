import fastapi
from fastapi.middleware.cors import CORSMiddleware
import time
import threading

import trovo
import twitch
import youtube

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

streams_lock = threading.Lock()

UPDATE_INTERVAL = 60 * 5
YOUTUBE_FULL_UPDATE_INTERVAL = 3
TWITCH_RESET_USER_THUMBNAILS_INTERVAL = 200

streams = []


def update_streams():
    global streams
    youtube_full_update_counter = 0
    twitch_reset_user_thumbnails_counter = 0

    while True:
        start = time.time()
        print(f'updating streams.. time: {time.ctime()}')

        twitch.update_twitch_streams()
        new_streams = twitch.get_streams()

        if youtube_full_update_counter == 0:
            youtube.update_youtube_streams()
        else:
            youtube.update_youtube_current_streams()

        new_streams += youtube.get_streams()

        #trovo.update_trovo_streams()
        #new_streams += trovo.get_streams()

        new_streams.sort(key=lambda x: x['viewer_count'], reverse=True)

        with streams_lock:
            streams = new_streams

        youtube_full_update_counter += 1
        if youtube_full_update_counter == YOUTUBE_FULL_UPDATE_INTERVAL:
            youtube_full_update_counter = 0

        twitch_reset_user_thumbnails_counter += 1
        if twitch_reset_user_thumbnails_counter == TWITCH_RESET_USER_THUMBNAILS_INTERVAL:
            twitch.reset_user_thumbnails()
            twitch_reset_user_thumbnails_counter = 0

        exec_time = time.time() - start
        print(f'streams updated in {round(exec_time, 3)} secs')

        time.sleep(UPDATE_INTERVAL - exec_time)


@app.on_event("startup")
def start_up():
    print('starting up..')
    update_thread = threading.Thread(target=update_streams)
    update_thread.start()


@app.get("/streams")
def get_streams():
    global streams

    with streams_lock:
        return streams


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info")
