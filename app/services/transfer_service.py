from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime, time

from app.models.domain import Card, Account, Transaction, TransactionType, TransactionStatus
from app.core.config import settings
from app.core.security import verify_password


async def process_transfer(
    db: AsyncSession,
    source_card_num: str,
    dest_card_num: str,
    amount: int,
    pin: str
):
    if source_card_num == dest_card_num:
        raise HTTPException(status_code=400, detail="Source and destination cards cannot be the same")

    async with db.begin():
        source_q = await db.execute(
            select(Card, Account)
            .join(Account, Card.account_id == Account.id)
            .where(Card.card_number == source_card_num)
            .with_for_update()
        )
        source_data = source_q.first()

        if not source_data:
            raise HTTPException(status_code=404, detail="Source card not found")

        src_card, src_account = source_data

        if not verify_password(pin, src_card.hashed_pin):
            raise HTTPException(status_code=403, detail="Invalid PIN")

        dest_q = await db.execute(
            select(Card, Account)
            .join(Account, Card.account_id == Account.id)
            .where(Card.card_number == dest_card_num)
            .with_for_update()
        )
        dest_data = dest_q.first()

        if not dest_data:
            raise HTTPException(status_code=404, detail="Destination card not found")

        dst_card, dst_account = dest_data

        calculated_fee = int(amount * settings.TRANSACTION_FEE_PERCENTAGE)
        fee = min(calculated_fee, settings.MAX_TRANSACTION_FEE)

        total_deduction = amount + fee

        if src_account.balance < total_deduction:
            raise HTTPException(status_code=400, detail="Insufficient account balance")

        today_start = datetime.combine(datetime.now().date(), time.min)

        daily_sum_q = await db.execute(
            select(func.sum(Transaction.amount))
            .where(
                and_(
                    Transaction.source_card_id == src_card.id,
                    Transaction.created_at >= today_start,
                    Transaction.status == TransactionStatus.SUCCESS.value,
                    Transaction.type == TransactionType.CARD_TO_CARD.value
                )
            )
        )
        current_daily_sum = daily_sum_q.scalar() or 0

        if (current_daily_sum + amount) > settings.DAILY_TRANSACTION_LIMIT:
            raise HTTPException(status_code=400, detail="Daily transaction limit (50,000,000 Tomans) has been reached")

        src_account.balance -= total_deduction
        dst_account.balance += amount

        new_tx = Transaction(
            source_card_id=src_card.id,
            dest_card_id=dst_card.id,
            amount=amount,
            fee_amount=fee,
            total_amount=total_deduction,
            type=TransactionType.CARD_TO_CARD.value,
            status=TransactionStatus.SUCCESS.value,
            ref_number=f"TRX-{int(datetime.now().timestamp() * 1000)}",
            description="Card-to-card transfer"
        )
        db.add(new_tx)

        return {
            "ref_number": new_tx.ref_number,
            "amount": amount,
            "fee": fee,
            "status": "SUCCESS",
            "date": datetime.now(),
            "type": "transfer",
            "source": src_card.card_number,
            "destination": dst_card.card_number
        }
