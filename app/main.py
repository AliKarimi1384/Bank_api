from fastapi import FastAPI,HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings
from app.api.v1.endpoints import cards

#api key
API_KEY_NAME = "x-api-key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != settings.API_KEY:
        raise HTTPException(
            status_code=403, detail="دسترسی غیرمجاز: API Key نامعتبر است"
        )
    return api_key_header

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="سیستم بانکی",
    version="1.0.0"
)

#roots
app.include_router(cards.router, prefix="/api/v1/cards", tags=["Cards"], dependencies=[Depends(get_api_key)])

@app.get("/")
async def root():
    return {"message": "Bank API is running!"}