import fastapi
import time
import twitch
import youtube
import threading


app = fastapi.FastAPI()
refresh_interval = 5 * 60
lock = threading.Lock()


streams = []


def update_streams():
    global streams

    new_streams = twitch.get_streams() + youtube.get_streams()
    new_streams.sort(key=lambda x: x['viewer_count'], reverse=True)

    with lock:
        streams = new_streams


def background_update():
    threading.Timer(refresh_interval, background_update).start()


@app.on_event("startup")
def startup_event():
    threading.Timer(0, background_update).start()


@app.get("/streams")
def streams():
    global streams
    with lock:
        return {
            "len": len(streams),
            "streams": streams
        }