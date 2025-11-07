#!/usr/bin/env python3
import sqlite3
import sys
import os

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH

def check_quota_table_structure():
    """Check the structure of the quota table"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute('PRAGMA table_info(quota)')
        print("Table structure for quota:")
        print("-" * 50)
        for col in cursor.fetchall():
            print(f"Column {col[0]}: {col[1]} ({col[2]})")
        
        # Check a sample record
        cursor.execute("SELECT * FROM quota WHERE 类别1 = '绕嵌排' AND 定额 = 4 LIMIT 1")
        row = cursor.fetchone()
        if row:
            print("\nSample record structure:")
            print("-" * 50)
            cursor.execute("SELECT * FROM quota WHERE 类别1 = '绕嵌排' AND 定额 = 4 LIMIT 1")
            columns = [description[0] for description in cursor.description]
            print("Columns:", columns)
            print("Sample data:", dict(zip(columns, row)))
            
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_quota_table_structure()
