# scripts/migrate_add_symbol.py
from sqlalchemy import text
from src.database import get_db_session

def migrate():
    with get_db_session() as db:
        # 0. Count existing trades for validation
        initial_count = db.execute(text("SELECT COUNT(*) FROM trades")).scalar()
        print(f"Found {initial_count} existing trades")
        
        # 1. Add nullable column
        print("Adding symbol column (nullable)...")
        db.execute(text("ALTER TABLE trades ADD COLUMN IF NOT EXISTS symbol VARCHAR(20)"))
        db.execute(text("ALTER TABLE strategies ADD COLUMN IF NOT EXISTS symbol VARCHAR(20)"))
        
        # 2. Backfill legacy data
        print("Backfilling legacy data with 'BTCUSDT'...")
        db.execute(text("UPDATE trades SET symbol = 'BTCUSDT' WHERE symbol IS NULL"))
        db.execute(text("UPDATE strategies SET symbol = 'BTCUSDT' WHERE symbol IS NULL"))
        
        # 3. Set NOT NULL
        print("Setting NOT NULL constraint...")
        db.execute(text("ALTER TABLE trades ALTER COLUMN symbol SET NOT NULL"))
        db.execute(text("ALTER TABLE strategies ALTER COLUMN symbol SET NOT NULL"))
        
        # 4. Create indexes
        print("Creating indexes...")
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades(symbol)"))
        db.execute(text("CREATE INDEX IF NOT EXISTS idx_strategies_symbol ON strategies(symbol)"))
        
        db.commit()
        
        # 5. Verify migration
        migrated_count = db.execute(text("SELECT COUNT(*) FROM trades WHERE symbol = 'BTCUSDT'")).scalar()
        assert migrated_count == initial_count, f"Expected {initial_count} trades, got {migrated_count}"
        print(f"✓ Verified {migrated_count} legacy trades migrated correctly")
        print("✓ Migration complete")

if __name__ == "__main__":
    migrate()
