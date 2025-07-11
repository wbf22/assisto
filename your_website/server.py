
import asyncio
from contextlib import asynccontextmanager
import os
import signal
import webbrowser
from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
import uvicorn


# shut down when parent is killed
@asynccontextmanager
async def monitor_parent(app: FastAPI):
    ppid = os.getppid()

    async def watch_parent():
        while True:
            await asyncio.sleep(1)
            if os.getppid() != ppid:
                print("Parent process died. Shutting down.")
                os.kill(os.getpid(), signal.SIGTERM)

    task = asyncio.create_task(watch_parent())
    yield  # Yield control to allow startup to complete
    task.cancel()  # Cleanup when FastAPI shuts down


app = FastAPI(lifespan=monitor_parent)

@app.get("/assisto_edit")
async def download_file():
    file_path = "../editor/editor.html"
    return FileResponse(file_path)

app.mount("/", StaticFiles(directory="."), name="static")


if __name__ == "__main__":
    url = 'http://127.0.0.1:8000/assisto_edit'
    webbrowser.open(url)

    uvicorn.run(app, host="127.0.0.1", port=8000)
    