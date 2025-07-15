from fastapi import FastAPI
from api.routes import router
from services.indexer import Indexer
from services.drive_client import DriveClient
import asyncio

app = FastAPI(title="File Search Service")

# Initialize services
drive_client = DriveClient()
indexer = Indexer()

# Include API routes
app.include_router(router)

# Initialize indexing on startup
@app.on_event("startup")
async def startup_event():
    files = drive_client.list_files()
    for file in files:
        content = drive_client.download_file_content(file)
        indexer.index_file(file, content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)