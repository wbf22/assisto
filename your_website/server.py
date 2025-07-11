
import asyncio
from contextlib import asynccontextmanager
import os
import signal
from fastapi import FastAPI
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

app.mount("/", StaticFiles(directory="."), name="static")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)