import asyncio
import random
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.domain import (
    User,
    Account,
    Card,
    Transaction,
    TransactionType,
    TransactionStatus,
    EntityStatus,
)
from app.core.security import get_password_hash
from datetime import datetime, timedelta

NUM_USERS = 10
NUM_TRANSACTIONS = 100_000

async def seed_data():
    async with AsyncSessionLocal() as session:
        print("🌱 Start seeding database...")

        hashed_pin_1234 = get_password_hash("1234")

        print("👤 Creating Users...")
        result = await session.execute(select(User))
        if result.scalars().first():
            print("⚠️  Data already exists! You might want to drop tables first.")
            return

        users = []
        for i in range(NUM_USERS):
            user = User(
                full_name=f"User {i}",
                mobile=f"0912000000{i}",
                national_id=f"111111111{i}",
            )
            users.append(user)
        session.add_all(users)
        await session.commit()

        user_result = await session.execute(select(User))
        db_users = user_result.scalars().all()

        print("💳 Creating Accounts & Cards (1-3 per user)...")
        cards = []

        for user in db_users:
            num_cards = random.randint(1, 3)

            for j in range(num_cards):
                account = Account(
                    user_id=user.id,
                    iban=f"IR0000000000000000{user.id:02d}{j:02d}",
                    balance=random.randint(10_000_000, 100_000_000),
                    status=EntityStatus.ACTIVE.value,
                )
                session.add(account)
                await session.flush()

                card = Card(
                    user_id=user.id,
                    account_id=account.id,
                    card_number=f"60379911{user.id:04d}{j:04d}",
                    cvv2="1234",
                    expire_month=12,
                    expire_year=1405,
                    status=EntityStatus.ACTIVE.value,
                    hashed_pin=hashed_pin_1234,
                )
                cards.append(card)

        session.add_all(cards)
        await session.commit()
        print(f"✅ Created {len(cards)} cards for {NUM_USERS} users.")

        print(f"💸 Generating {NUM_TRANSACTIONS} Transactions...")

        card_result = await session.execute(select(Card))
        db_cards = card_result.scalars().all()

        transactions_batch = []
        for i in range(NUM_TRANSACTIONS):
            src = random.choice(db_cards)
            dst = random.choice(db_cards)

            amount = random.randint(1000, 500_000)
            fee = int(amount * 0.001)

            tx = Transaction(
                source_card_id=src.id,
                dest_card_id=dst.id,
                amount=amount,
                fee_amount=fee,
                total_amount=amount + fee,
                type=TransactionType.CARD_TO_CARD.value,
                status=TransactionStatus.SUCCESS.value,
                ref_number=str(random.randint(100000000000, 999999999999)),
                created_at=datetime.now() - timedelta(days=10)
            )
            transactions_batch.append(tx)

            if len(transactions_batch) >= 5000:
                session.add_all(transactions_batch)
                await session.commit()
                transactions_batch = []
                print(".", end="", flush=True)

        if transactions_batch:
            session.add_all(transactions_batch)
            await session.commit()

        print("\n✅ Done! Database seeded successfully.")

if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(seed_data())
