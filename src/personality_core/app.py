from fastapi import FastAPI
from personality_core.server.routes import router

api = FastAPI(title="Personality Core", version="0.1.0")
api.include_router(router)
