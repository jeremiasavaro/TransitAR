# This file is the main entry point for the FastAPI application.
# It creates an instance of the FastAPI class and includes the routers for different API endpoints.
# The routers are currently commented out, but they can be uncommented to enable the corresponding routes.

from fastapi import FastAPI

# from app.api.routes import chat, trips

app = FastAPI()

# app.include_router(chat.router)
# app.include_router(trips.router)
