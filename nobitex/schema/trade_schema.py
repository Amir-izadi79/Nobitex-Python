from decimal import Decimal
from typing import List, Any, Literal, Dict
from datetime import datetime

from pydantic import BaseModel, Field, TypeAdapter, field_validator, ConfigDict

class TradeEntry(BaseModel):

    market: str = Field(..., description="Trading Pair Market")
    price: Decimal = Field(..., description="Trade Price")
    amount: Decimal = Field(..., description="Trade Amount")
    total: Decimal = Field(..., description="Total Value (price * amount)")
    type: Literal['buy', 'sell'] = Field(..., description="Trade Type")
    timestamp: str = Field(..., description="Trade Timestamp")

    @field_validator('timestamp', mode='before')
    @classmethod
    def validate_timestamp(cls, v: Any) -> str:
        if isinstance(v, datetime):
            return v.isoformat()
        return str(v)
    
class NubitexTrades(BaseModel):

    trades: List[TradeEntry] = Field(..., description="List of Trade Entries")
    status: str = Field(..., description="Response Status")

all_trades_T = TypeAdapter(Dict[str, NubitexTrades])