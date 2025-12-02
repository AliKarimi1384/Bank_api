from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from app.core.config import settings


class CardResponse(BaseModel):
    card_number: str
    iban: str = Field(..., alias="account_number")
    balance: int

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    ref_number: str
    amount: int
    fee: int
    status: str
    date: datetime
    type: str

    class Config:
        from_attributes = True


class TransferRequest(BaseModel):
    source_card_number: str = Field(..., min_length=16, max_length=16)
    dest_card_number: str = Field(..., min_length=16, max_length=16)
    amount: int
    pin: str

    @validator("amount")
    def validate_amount(cls, v):
        if v < settings.MIN_TRANSACTION_AMOUNT:
            raise ValueError(f"حداقل مبلغ تراکنش {settings.MIN_TRANSACTION_AMOUNT} تومان است")
        if v > settings.MAX_TRANSACTION_AMOUNT:
            raise ValueError(f"حداکثر مبلغ تراکنش {settings.MAX_TRANSACTION_AMOUNT} تومان است")
        return v


class WithdrawRequest(BaseModel):
    card_number: str
    amount: int
    pin: str

    @validator("amount")
    def validate_amount(cls, v):
        if v < settings.MIN_TRANSACTION_AMOUNT:
            raise ValueError("مبلغ کمتر از حد مجاز است")
        return v
