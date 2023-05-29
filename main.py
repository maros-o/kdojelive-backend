import fastapi
import time
import twitch
import youtube
import threading


app = fastapi.FastAPI()
lock = threading.Lock()

UPDATE_INTERVAL = 60 * 5
YOUTUBE_FULL_UPDATE_CYCLES = 3

streams = []


def update_streams():
    global streams

    youtube_full_update_counter = 0

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

        new_streams.sort(key=lambda x: x['viewer_count'], reverse=True)

        with lock:
            streams = new_streams

        youtube_full_update_counter += 1
        if youtube_full_update_counter == YOUTUBE_FULL_UPDATE_CYCLES:
            youtube_full_update_counter = 0

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

    with lock:
        return streams


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
