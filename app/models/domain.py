from sqlalchemy import Column, Integer, String, BigInteger, ForeignKey, DateTime, Text, SmallInteger, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

#enums
class TransactionType(int, enum.Enum):
    WITHDRAW = 1
    CARD_TO_CARD = 2

class TransactionStatus(int, enum.Enum):
    PENDING = 0
    SUCCESS = 1
    FAILED = 2

class EntityStatus(int, enum.Enum):
    ACTIVE = 1
    BLOCKED = 0

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=True)
    mobile = Column(String(11), unique=True, index=True, nullable=False)
    national_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    accounts = relationship("Account", back_populates="owner")
    cards = relationship("Card", back_populates="owner")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    iban = Column(String, unique=True, nullable=True)
    balance = Column(BigInteger, default=0, nullable=False)
    status = Column(SmallInteger, default=EntityStatus.ACTIVE.value)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="accounts")
    cards = relationship("Card", back_populates="account")

class Card(Base):
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    
    card_number = Column(String(16), unique=True, index=True, nullable=False)
    cvv2 = Column(String(4), nullable=False)
    expire_month = Column(SmallInteger, nullable=False)
    expire_year = Column(SmallInteger, nullable=False)
    status = Column(SmallInteger, default=EntityStatus.ACTIVE.value)
    
    hashed_pin = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="cards")
    account = relationship("Account", back_populates="cards")
    
    sent_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.source_card_id",
        back_populates="source_card"
    )
    received_transactions = relationship(
        "Transaction",
        foreign_keys="Transaction.dest_card_id",
        back_populates="dest_card"
    )

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    
    source_card_id = Column(Integer, ForeignKey("cards.id"), nullable=True)
    dest_card_id = Column(Integer, ForeignKey("cards.id"), nullable=True)
    
    amount = Column(BigInteger, nullable=False)
    fee_amount = Column(BigInteger, default=0)
    total_amount = Column(BigInteger, nullable=False)
    
    type = Column(SmallInteger, nullable=False)
    status = Column(SmallInteger, default=TransactionStatus.PENDING.value)
    
    ref_number = Column(String, unique=True, index=True, nullable=True)
    description = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    source_card = relationship(
        "Card",
        foreign_keys=[source_card_id],
        back_populates="sent_transactions"
    )
    dest_card = relationship(
        "Card",
        foreign_keys=[dest_card_id],
        back_populates="received_transactions"
    )

    __table_args__ = (
        Index('idx_source_created', 'source_card_id', 'created_at'),
        Index('idx_dest_created', 'dest_card_id', 'created_at'),
        Index('idx_status_created', 'status', 'created_at'),
        Index('idx_created_at', 'created_at'),
    )
