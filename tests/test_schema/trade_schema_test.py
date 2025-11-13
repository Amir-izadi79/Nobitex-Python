"""
Tests for trade_schema.py (Nubitex Format)

schema uses Nubitex format with fields:
- market, price, amount, total, type, timestamp
"""

import pytest
from decimal import Decimal
from datetime import datetime
from trade_schema import TradeEntry, NubitexTrades, all_trades_T


class TestTradeEntry:

    
    def test_parses_dict_format(self):

        trade = TradeEntry.model_validate({
            "market": "Bitcoin-USDT",
            "price": "50000.5",
            "amount": "0.1",
            "total": "5000.05",
            "type": "buy",
            "timestamp": "2024-01-01T10:00:00+00:00"
        })
        
        assert trade.market == "Bitcoin-USDT"
        assert trade.price == Decimal("50000.5")
        assert trade.amount == Decimal("0.1")
        assert trade.total == Decimal("5000.05")
        assert trade.type == "buy"
        assert "2024-01-01" in trade.timestamp
    
    def test_buy_type(self):

        trade = TradeEntry.model_validate({
            "market": "BTC-USDT",
            "price": "50000",
            "amount": "0.1",
            "total": "5000",
            "type": "buy",
            "timestamp": "2024-01-01T10:00:00+00:00"
        })
        assert trade.type == "buy"
    
    def test_sell_type(self):
        
        trade = TradeEntry.model_validate({
            "market": "BTC-USDT",
            "price": "50000",
            "amount": "0.1",
            "total": "5000",
            "type": "sell",
            "timestamp": "2024-01-01T10:00:00+00:00"
        })
        assert trade.type == "sell"
    
    def test_rejects_invalid_type(self):
        
        with pytest.raises(Exception):
            TradeEntry.model_validate({
                "market": "BTC-USDT",
                "price": "50000",
                "amount": "0.1",
                "total": "5000",
                "type": "invalid",
                "timestamp": "2024-01-01T10:00:00+00:00"
            })
    
    def test_preserves_decimal_precision(self):
        
        trade = TradeEntry.model_validate({
            "market": "BTC-USDT",
            "price": "50000.123456789",
            "amount": "0.987654321",
            "total": "49350.4917",
            "type": "buy",
            "timestamp": "2024-01-01T10:00:00+00:00"
        })
        
        assert str(trade.price) == "50000.123456789"
        assert str(trade.amount) == "0.987654321"


class TestNubitexTrades:
    
    def test_parses_multiple_trades(self):
        
        trades = NubitexTrades.model_validate({
            "trades": [
                {
                    "market": "BTC-USDT",
                    "price": "50000",
                    "amount": "0.1",
                    "total": "5000",
                    "type": "buy",
                    "timestamp": "2024-01-01T10:00:00+00:00"
                },
                {
                    "market": "BTC-USDT",
                    "price": "50001",
                    "amount": "0.2",
                    "total": "10000.2",
                    "type": "sell",
                    "timestamp": "2024-01-01T10:00:01+00:00"
                }
            ],
            "status": "ok"
        })
        
        assert len(trades.trades) == 2
        assert trades.trades[0].type == "buy"
        assert trades.trades[1].type == "sell"
        assert trades.status == "ok"
    
    def test_empty_trades_list(self):
        
        trades = NubitexTrades.model_validate({
            "trades": [],
            "status": "ok"
        })
        assert len(trades.trades) == 0


class TestRealNubitexFormat:
    
    def test_nubitex_api_format(self):
        
        api_response = {
            "trades": [
                {
                    "market": "Bitcoin-﷼",
                    "total": "99949293.63720000000000000000",
                    "price": "750032220.0000000000",
                    "amount": "0.1332600000",
                    "type": "buy",
                    "timestamp": "2018-11-18T11:56:07.798845+00:00"
                }
            ],
            "status": "ok"
        }
        
        trades = NubitexTrades.model_validate(api_response)
        
        assert trades.status == "ok"
        assert len(trades.trades) == 1
        assert trades.trades[0].market == "Bitcoin-﷼"
        assert trades.trades[0].type == "buy"


if __name__ == "__main__":
    print("\n" + "="*60)
    print("NUBITEX TRADE SCHEMA TESTS")
    print("="*60 + "\n")
    
    pytest.main([__file__, "-v", "--tb=short"])