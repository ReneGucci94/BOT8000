import sys
from src.database import get_db_session
from src.database.models import Strategy, Pattern, Trade
from sqlalchemy import func

def verify_results():
    print("--- 🔍 RESULTS VERIFICATION AUDIT ---")
    
    with get_db_session() as db:
        # 1. Audit Approved Strategies
        strategies = db.query(Strategy).filter(Strategy.status == 'APPROVED').all()
        print(f"\n[1] APPROVED STRATEGIES: {len(strategies)}")
        if not strategies:
            print("❌ No approved strategies found (despite dashboard saying 8?)")
        
        for s in strategies:
            print(f"   ► {s.name}")
            print(f"     PF: {s.profit_factor} | WR: {s.win_rate}%")
            print(f"     Params: {s.parameters}")
            print(f"     Filters: {s.filters}")
            
            # Sanity Check: Is PF realistic?
            if s.profit_factor is not None and float(s.profit_factor) > 10.0:
                print("     ⚠️ WARNING: Suspiciously high Profit Factor (Look-ahead bias?)")
            
        # 2. Audit Patterns
        patterns = db.query(Pattern).filter(Pattern.is_active == True).all()
        print(f"\n[2] DETECTED FAILURE PATTERNS: {len(patterns)}")
        for p in patterns:
            print(f"   ► Type: {p.pattern_type}")
            print(f"     WR in context: {p.win_rate}% (Samples: {p.sample_size})")
            print(f"     Conditions: {p.conditions}")

        # 3. Audit Trade Integrity (Sample)
        trades_count = db.query(func.count(Trade.id)).scalar()
        print(f"\n[3] TOTAL TRADES RECORDED: {trades_count}")
        
        # Check for Look-ahead bias in a sample trade
        # Entry time should be >= Candle timestamp (which usually denotes Open time or Close time? need to verify)
        # Binance klines uses Open Time. So Close Time is Timestamp + Timeframe_ms - 1.
        # If we trade at Close of candle T, our trade timestamp should be T + 4h.
        
        sample_trade = db.query(Trade).order_by(Trade.timestamp.desc()).first()
        if sample_trade:
            print(f"\n   ► LATEST TRADE AUDIT:")
            print(f"     Pair: {sample_trade.pair}")
            print(f"     Timestamp (Signal): {sample_trade.timestamp}")
            print(f"     Entry: {sample_trade.entry_price}")
            print(f"     Result: {sample_trade.result}")
            print(f"     Market State Keys: {list(sample_trade.market_state.keys()) if sample_trade.market_state else 'None'}")
            
    print("\n--- ✅ AUDIT COMPLETE ---")

if __name__ == "__main__":
    verify_results()
