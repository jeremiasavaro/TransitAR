from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
async def chat():
    """
    Endpoint to handle chat messages.
    """
    return {"message": "Chat endpoint is under construction."}
