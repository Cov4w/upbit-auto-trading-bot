import sqlite3
import pandas as pd
import os

DB_PATH = "data/trade_memory.db"

def clean_database():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 1. 전체 데이터 수 확인
        cursor.execute("SELECT COUNT(*) FROM trades")
        total_before = cursor.fetchone()[0]
        print(f"📊 Total Records Before: {total_before}")
        
        # 2. NULL 값을 가진 레코드 확인 (rsi_change는 새로 추가된 컬럼)
        # 새로 추가된 컬럼 중 하나라도 NULL이면 삭제 대상
        cursor.execute("""
            SELECT COUNT(*) FROM trades 
            WHERE rsi_change IS NULL 
               OR volume_trend IS NULL
               OR profit_class IS NULL
        """)
        null_count = cursor.fetchone()[0]
        print(f"🗑️ Records with NULL features: {null_count}")
        
        if null_count > 0:
            # 3. NULL 데이터 삭제
            cursor.execute("""
                DELETE FROM trades 
                WHERE rsi_change IS NULL 
                   OR volume_trend IS NULL
                   OR profit_class IS NULL
            """)
            conn.commit()
            print(f"✅ Deleted {null_count} records.")
        else:
            print("✨ No NULL records found.")
            
        # 4. 삭제 후 데이터 수 확인
        cursor.execute("SELECT COUNT(*) FROM trades")
        total_after = cursor.fetchone()[0]
        print(f"📊 Total Records After: {total_after}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")

if __name__ == "__main__":
    clean_database()
