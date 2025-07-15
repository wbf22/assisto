
import asyncio
from contextlib import asynccontextmanager
import os
import signal
import webbrowser
from fastapi import FastAPI, Response
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
import uvicorn


file_history = []
undone_history = []


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

@app.post("/update_files")
async def update_files(files: dict):
    file_history.append(files)

    # update files
    for [file_path, contents] in files.items():
        with open(file_path, 'w') as file:
            file.write(contents)

    return Response(status_code=204)
    

@app.get("/get_files")
async def get_files():
    files = {}
    for filename in os.listdir("."):
        file_path = os.path.join(".", filename)
        if filename != 'server.py' and os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                contents = file.read()
                files[filename] = contents

    return files


class NoCacheStaticFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        # Set headers to disable caching
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
app.mount("/", NoCacheStaticFiles(directory="."), name="static")




if __name__ == "__main__":
    url = 'http://127.0.0.1:8000/assisto_edit'
    webbrowser.open(url)

    uvicorn.run(app, host="127.0.0.1", port=8000)
    