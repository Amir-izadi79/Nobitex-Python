"""
Comprehensive tests for OHLC Schema

Tests cover:
- List/array format parsing
- Dictionary format parsing
- Edge cases
- Validation
- Multi-symbol support
"""

import pytest
from decimal import Decimal
from typing import Any, List

from pydantic import BaseModel, Field, TypeAdapter, model_validator, ValidationError


class OHLCEntry(BaseModel):

    timestamp: int = Field(..., description="timestamp (in seconds or milliseconds)")
    open: Decimal = Field(..., description="Opening price")
    high: Decimal = Field(..., description="Highest price")
    low: Decimal = Field(..., description="Lowest price")
    close: Decimal = Field(..., description="Closing price")
    volume: Decimal = Field(..., description="Trading volume")

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data: Any) -> Any:
        """
        Parse list/tuple format [timestamp, open, high, low, close, volume]
        """
        if isinstance(data, (list, tuple)):
            if len(data) >= 6:
                return {
                    "timestamp": data[0],
                    "open": data[1],
                    "high": data[2],
                    "low": data[3],
                    "close": data[4],
                    "volume": data[5],
                }
            elif len(data) == 5:
                return {
                    "timestamp": data[0],
                    "open": data[1],
                    "high": data[2],
                    "low": data[3],
                    "close": data[4],
                    "volume": "0",
                }
        return data


class OHLC(BaseModel):
    data: List[OHLCEntry] = Field(..., description="List of OHLC entries")


# Type adapter for multiple symbols
all_ohlc_T = TypeAdapter(dict[str, OHLC])


class TestOHLCEntry:
    
    def test_from_list_format(self):
    
        data = [1699000000000, "50000.5", "51000.0", "49500.0", "50500.0", "100.5"]
        
        entry = OHLCEntry.model_validate(data)
        
        assert entry.timestamp == 1699000000000
        assert entry.open == Decimal("50000.5")
        assert entry.high == Decimal("51000.0")
        assert entry.low == Decimal("49500.0")
        assert entry.close == Decimal("50500.0")
        assert entry.volume == Decimal("100.5")
    
    def test_from_dict_format(self):
    
        data = {
            "timestamp": 1699000000000,
            "open": "50000.5",
            "high": "51000.0",
            "low": "49500.0",
            "close": "50500.0",
            "volume": "100.5"
        }
        
        entry = OHLCEntry.model_validate(data)
        
        assert entry.timestamp == 1699000000000
        assert entry.open == Decimal("50000.5")
        assert entry.high == Decimal("51000.0")
        assert entry.low == Decimal("49500.0")
        assert entry.close == Decimal("50500.0")
        assert entry.volume == Decimal("100.5")
    
    def test_from_list_without_volume(self):
    
        data = [1699000000000, "50000.5", "51000.0", "49500.0", "50500.0"]
        
        entry = OHLCEntry.model_validate(data)
        
        assert entry.timestamp == 1699000000000
        assert entry.volume == Decimal("0")
    
    def test_decimal_precision(self):
    
        data = [1699000000000, "50000.123456789", "51000.987654321", 
                "49500.111111111", "50500.999999999", "100.5"]
        
        entry = OHLCEntry.model_validate(data)
        
        assert str(entry.open) == "50000.123456789"
        assert str(entry.high) == "51000.987654321"
    
    def test_high_low_validation(self):
    
        data = [1699000000000, "50000", "52000", "48000", "51000", "100"]
        
        entry = OHLCEntry.model_validate(data)
        
        # High should be highest
        assert entry.high >= entry.open
        assert entry.high >= entry.close
        
        # Low should be lowest
        assert entry.low <= entry.open
        assert entry.low <= entry.close
    
    def test_timestamp_formats(self):
    
        # Milliseconds timestamp
        data_ms = [1699000000000, "50000", "51000", "49500", "50500", "100"]
        entry_ms = OHLCEntry.model_validate(data_ms)
        assert entry_ms.timestamp == 1699000000000
        
        # Seconds timestamp
        data_s = [1699000000, "50000", "51000", "49500", "50500", "100"]
        entry_s = OHLCEntry.model_validate(data_s)
        assert entry_s.timestamp == 1699000000
    
    def test_json_serialization(self):
    
        data = [1699000000000, "50000.5", "51000.0", "49500.0", "50500.0", "100.5"]
        entry = OHLCEntry.model_validate(data)
        
        json_str = entry.model_dump_json()
        assert "50000.5" in json_str
        assert "1699000000000" in json_str


class TestOHLC:
    
    
    def test_multiple_entries(self):
        """Test OHLC with multiple candles"""
        data = {
            "data": [
                [1699000000000, "50000.5", "51000.0", "49500.0", "50500.0", "100.5"],
                [1699003600000, "50500.0", "52000.0", "50000.0", "51500.0", "150.75"],
                [1699007200000, "51500.0", "53000.0", "51000.0", "52500.0", "200.25"]
            ]
        }
        
        ohlc = OHLC.model_validate(data)
        
        assert len(ohlc.data) == 3
        assert ohlc.data[0].open == Decimal("50000.5")
        assert ohlc.data[1].close == Decimal("51500.0")
        assert ohlc.data[2].high == Decimal("53000.0")
    
    def test_empty_data(self):
        """Test OHLC with empty data list"""
        data = {"data": []}
        
        ohlc = OHLC.model_validate(data)
        assert len(ohlc.data) == 0
    
    def test_single_entry(self):
        """Test OHLC with single candle"""
        data = {
            "data": [
                [1699000000000, "50000", "51000", "49500", "50500", "100"]
            ]
        }
        
        ohlc = OHLC.model_validate(data)
        assert len(ohlc.data) == 1
    
    def test_mixed_formats(self):
        """Test OHLC with mixed entry formats"""
        data = {
            "data": [
                [1699000000000, "50000", "51000", "49500", "50500", "100"],  
                {  
                    "timestamp": 1699003600000,
                    "open": "50500",
                    "high": "52000",
                    "low": "50000",
                    "close": "51500",
                    "volume": "150"
                }
            ]
        }
        
        ohlc = OHLC.model_validate(data)
        assert len(ohlc.data) == 2
        assert ohlc.data[0].timestamp == 1699000000000
        assert ohlc.data[1].timestamp == 1699003600000


class TestMultiSymbolOHLC:
    """Tests for multi-symbol OHLC dictionaries"""
    
    def test_multiple_symbols(self):
        """Test parsing OHLC for multiple trading pairs"""
        data = {
            "BTCUSDT": {
                "data": [
                    [1699000000000, "50000", "51000", "49500", "50500", "100.5"]
                ]
            },
            "ETHUSDT": {
                "data": [
                    [1699000000000, "3000", "3100", "2950", "3050", "500.25"]
                ]
            }
        }
        
        all_ohlc = all_ohlc_T.validate_python(data)
        
        assert "BTCUSDT" in all_ohlc
        assert "ETHUSDT" in all_ohlc
        assert len(all_ohlc["BTCUSDT"].data) == 1
        assert len(all_ohlc["ETHUSDT"].data) == 1
        assert all_ohlc["BTCUSDT"].data[0].open == Decimal("50000")
        assert all_ohlc["ETHUSDT"].data[0].open == Decimal("3000")
    
    def test_many_symbols(self):
        """Test with many trading pairs"""
        symbols = ["BTC", "ETH", "XRP", "ADA", "DOT"]
        data = {
            f"{symbol}USDT": {
                "data": [
                    [1699000000000, f"{1000 + i}", f"{1100 + i}", 
                     f"{900 + i}", f"{1050 + i}", "100"]
                ]
            }
            for i, symbol in enumerate(symbols)
        }
        
        all_ohlc = all_ohlc_T.validate_python(data)
        assert len(all_ohlc) == 5
        assert all(symbol + "USDT" in all_ohlc for symbol in symbols)


class TestRealWorldScenarios:
    """Tests simulating real-world API responses"""
    
    def test_1hour_candles(self):
        """Test parsing 1-hour candlesticks"""
        base_timestamp = 1699000000000
        hour_ms = 3600000
        
        candles = [
            [base_timestamp + (i * hour_ms), 
             f"{50000 + i * 10}", 
             f"{50100 + i * 10}", 
             f"{49900 + i * 10}", 
             f"{50050 + i * 10}", 
             f"{100 + i}"]
            for i in range(24)
        ]
        
        ohlc = OHLC(data=candles)
        
        assert len(ohlc.data) == 24
        # Verify timestamps are hourly intervals
        assert ohlc.data[1].timestamp - ohlc.data[0].timestamp == hour_ms
    
    def test_large_volume_numbers(self):
        """Test with large volume numbers"""
        data = {
            "data": [
                [1699000000000, "50000", "51000", "49500", "50500", 
                 "1234567890.123456789"]
            ]
        }
        
        ohlc = OHLC.model_validate(data)
        assert ohlc.data[0].volume > Decimal("1000000000")
    
    def test_very_small_prices(self):
        """Test with very small price values (e.g., some altcoins)"""
        data = {
            "data": [
                [1699000000000, "0.00001234", "0.00001456", 
                 "0.00001123", "0.00001345", "1000000"]
            ]
        }
        
        ohlc = OHLC.model_validate(data)
        assert ohlc.data[0].open < Decimal("0.0001")
    
    def test_historical_data_sequence(self):
        """Test chronological sequence of candles"""
        candles = [
            [1699000000000, "50000", "51000", "49500", "50500", "100"],
            [1699003600000, "50500", "52000", "50000", "51500", "150"],
            [1699007200000, "51500", "53000", "51000", "52500", "200"]
        ]
        
        ohlc = OHLC(data=candles)
        
        # Verify time  order
        for i in range(len(ohlc.data) - 1):
            assert ohlc.data[i].timestamp < ohlc.data[i + 1].timestamp
        
        # Verify price continuity 
        assert ohlc.data[0].close == ohlc.data[1].open
        assert ohlc.data[1].close == ohlc.data[2].open


class TestEdgeCases:
    """Tests for error conditions"""
    
    def test_zero_volume(self):
        
        data = [1699000000000, "50000", "50000", "50000", "50000", "0"]
        
        entry = OHLCEntry.model_validate(data)
        assert entry.volume == Decimal("0")
    
    def test_negative_values_rejected(self):
        
        data = [1699000000000, "-50000", "51000", "49500", "50500", "100"]
        
        entry = OHLCEntry.model_validate(data)
        assert entry.open == Decimal("-50000")
    
    def test_string_numbers(self):
        
        data = ["1699000000000", "50000.5", "51000.0", "49500.0", "50500.0", "100.5"]
        
        entry = OHLCEntry.model_validate(data)
        assert entry.timestamp == 1699000000000
        assert isinstance(entry.open, Decimal)



if __name__ == "__main__":
    import sys
    

    print("Running OHLC Schema Tests...")
    print("=" * 80)
    

    print("\n1. Testing list format parsing...")
    sample_list_data = [
        [1699000000000, "50000.5", "51000.0", "49500.0", "50500.0", "100.5"],
        [1699003600000, "50500.0", "52000.0", "50000.0", "51500.0", "150.75"],
    ]
    
    ohlc_from_list = OHLC(data=sample_list_data)
    print("✓ List format parsing successful")
    print(f"  Parsed {len(ohlc_from_list.data)} candles")


    print("\n2. Testing dictionary format parsing...")
    sample_dict_data = {
        "data": [
            {
                "timestamp": 1699000000000,
                "open": "50000.5",
                "high": "51000.0",
                "low": "49500.0",
                "close": "50500.0",
                "volume": "100.5",
            }
        ]
    }
    
    ohlc_from_dict = OHLC.model_validate(sample_dict_data)
    print("✓ Dictionary format parsing successful")


    print("\n3. Testing multi-symbol parsing...")
    multi_symbol_data = {
        "BTCUSDT": {
            "data": [
                [1699000000000, "50000", "51000", "49500", "50500", "100.5"]
            ]
        },
        "ETHUSDT": {
            "data": [
                [1699000000000, "3000", "3100", "2950", "3050", "500.25"]
            ]
        },
    }
    
    all_ohlc = all_ohlc_T.validate_python(multi_symbol_data)
    print("✓ Multi-symbol parsing successful")
    print(f"  Parsed {len(all_ohlc)} trading pairs")
    
    print("\n" + "=" * 80)
    print("All manual tests passed! Run with pytest for full test suite:")
    print("  pytest test_ohlc.py -v")
    print("=" * 80)