from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.endpoints import cards

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="سیستم بانکی",
    version="1.0.0"
)

#roots
app.include_router(cards.router, prefix="/api/v1/cards", tags=["Cards"])

@app.get("/")
async def root():
    return {"message": "Bank API is running!"}