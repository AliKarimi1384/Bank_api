from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from app.core.database import get_db, AsyncSession
from app.models.domain import User, Card, Account
from app.schemas.api_schemas import CardResponse

router = APIRouter()

#cards data
@router.get("/my-cards", response_model=List[CardResponse])
async def get_my_cards(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Card)
        .options(selectinload(Card.account))
        .where(Card.user_id == user_id)
    )
    cards = result.scalars().all()

    if not cards:
        raise HTTPException(status_code=404, detail="کاربری با این مشخصات یافت نشد یا کارتی ندارد")

    response_data = []
    for card in cards:
        response_data.append(CardResponse(
            card_number=card.card_number,
            account_number=card.account.iban,
            balance=card.account.balance
        ))

    return response_data
