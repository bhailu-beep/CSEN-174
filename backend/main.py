import logging
import os
from contextlib import asynccontextmanager

from database.connection import DbConnection
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.log import ColourizedFormatter

# Setup Logging
colored_format = ColourizedFormatter('%(name)s %(levelprefix)s %(message)s')

colored_stream_handler = logging.StreamHandler()
colored_stream_handler.setFormatter(colored_format)

logger = logging.getLogger('completec-backend')
logger.addHandler(colored_stream_handler)
logger.setLevel(logging.DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await DbConnection.initialize()
    yield
    await DbConnection.cleanup()

app = FastAPI(title = 'CompleteC API', version = '1.0', description = 'Backend API for CompleteC', lifespan = lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["http://localhost:3000"],
    allow_credentials = True,
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers = [
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "X-CSRF-Token"
    ],
)

# Automatically import and include all routers
for file in os.listdir("./routers"):
    if file != "__init__.py" and file.endswith(".py"):
        router = __import__(f"routers.{file[:-3]}", fromlist = ["router"])
        app.include_router(router.router)
