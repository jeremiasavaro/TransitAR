from fastapi import FastAPI
from infrastructure.database.session import init_db
from routes import chat

app = FastAPI()

# Keep route registration in one place so new endpoints are added here.
app.include_router(chat.router)


@app.on_event("startup")
def startup() -> None:
    # Create tables on startup for the minimal local setup.
    init_db()
