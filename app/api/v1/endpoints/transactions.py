from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import List

from app.core.database import get_db
from app.schemas.api_schemas import TransferRequest, TransactionResponse, WithdrawRequest
from app.services.transfer_service import process_transfer
from app.models.domain import Transaction, Card, Account, TransactionType, TransactionStatus
from app.core.config import settings

router = APIRouter()


@router.post("/transfer", response_model=TransactionResponse)
async def transfer_money(
    request: TransferRequest,
    db: AsyncSession = Depends(get_db)
):
    return await process_transfer(
        db,
        request.source_card_number,
        request.dest_card_number,
        request.amount,
        request.pin
    )


@router.post("/withdraw", response_model=TransactionResponse)
async def withdraw_money(
    request: WithdrawRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Card, Account)
        .join(Account)
        .where(Card.card_number == request.card_number)
        .with_for_update()
    )
    data = result.first()

    if not data:
        raise HTTPException(status_code=404, detail="Card not found")

    card, account = data

    if account.balance < request.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    account.balance -= request.amount

    new_tx = Transaction(
        source_card_id=card.id,
        dest_card_id=None,
        amount=request.amount,
        fee_amount=0,
        total_amount=request.amount,
        type=TransactionType.WITHDRAW.value,
        status=TransactionStatus.SUCCESS.value,
        ref_number=f"WD-{func.now()}",
        description="Cash withdrawal"
    )
    db.add(new_tx)
    await db.commit()

    return {
        "ref_number": "WD-SUCCESS",
        "amount": request.amount,
        "fee": 0,
        "status": "SUCCESS",
        "date": "2023-01-01",
        "type": "withdraw"
    }


@router.get("/history/{card_number}", response_model=List[TransactionResponse])
async def get_card_history(
    card_number: str,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(Transaction)
        .join(Transaction.source_card)
        .where(Transaction.source_card.has(card_number=card_number))
        .order_by(desc(Transaction.created_at))
        .limit(10)
    )

    result = await db.execute(query)
    transactions = result.scalars().all()

    response = []
    for tx in transactions:
        response.append({
            "ref_number": tx.ref_number or "N/A",
            "amount": tx.amount,
            "fee": tx.fee_amount,
            "status": "SUCCESS" if tx.status == 1 else "FAILED",
            "date": tx.created_at,
            "type": "transfer" if tx.type == 2 else "withdraw"
        })

    return response


@router.get("/fees-report")
async def get_total_fees(
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(func.sum(Transaction.fee_amount))

    result = await db.execute(query)
    total_fees = result.scalar() or 0

    return {"total_fee_income": total_fees}
