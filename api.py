import fastapi
import time
import twitch
import youtube

app = fastapi.FastAPI()


@app.get("/streams")
def streams():
    start = time.time()

    streams = twitch.get_streams()
    streams += youtube.get_streams()

    return {
        "executing_time": f"{round(time.time() - start, 3)} seconds",
        "len": len(streams),
        "streams": streams}


@app.post("/add-youtube-channel/{channel_id}")
def add_youtube_channel(channel_id: str):
    return {"channel_id": channel_id}
