"""
Schema has been defined using Pydantic to validate the data format of Nubitex API

Also it should be checked with actual API response to ensure correctness

"""
from decimal import Decimal
from typing import List, Any
from pydantic import BaseModel, Field, TypeAdapter, model_validator


class OHCLEntry(BaseModel):

    timestamp: int = Field(..., description="Timestamp (in seconds or milliseconds")
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="Highest price")
    low: Decimal = Field(..., description="Lowest price")
    close: Decimal = Field(..., description="Closing price")
    volume: Decimal = Field(..., description="Trading volume")

    @model_validator(mode="before")
    def validate_high_low(self) -> 'OHCLEntry':
       if self.high < max(self.open, self.close):
           raise ValueError("High must be >= max(open, close)")
       if self.low > min(self.open, self.close):
           raise ValueError("Low must be <= min(open, close)")
       return self
    @classmethod
    def parse_list(cls, values: Any) -> Any:
        if isinstance(values, (list, tuple)):
            if len(values) >= 6:
                return {
                    "timestamp": values[0],
                    "open": values[1],
                    "high": values[2],
                    "low": values[3],
                    "close": values[4],
                    "volume": values[5],
                }
            elif len(values) == 5:
                return {
                    "timestamp": values[0],
                    "open": values[1],
                    "high": values[2],
                    "low": values[3],
                    "close": values[4],
                    "volume": Decimal("0"),
                }
        return values
    
class OHCL(BaseModel):

    values : list[OHCLEntry] = Field(..., description="List of OHCL entries")


all_ohlc_T = TypeAdapter(Any)

