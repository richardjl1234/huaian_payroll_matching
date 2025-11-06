#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from config import DATABASE_PATH

def query_quota_table():
    """
    Query the quota table from the database and return results as JSON objects
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        
        # Create a cursor object
        cursor = conn.cursor()
        
        # Query all records from the quota table
        cursor.execute("SELECT * FROM quota")
        
        # Fetch all rows
        rows = cursor.fetchall()
        
        # Convert rows to list of dictionaries (JSON objects)
        json_list = []
        for row in rows:
            json_list.append(dict(row))
        
        # Close the connection
        conn.close()
        
        return json_list
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    """
    Main function to execute the quota table query and display results
    """
    print("Querying quota table from database...")
    print(f"Database path: {DATABASE_PATH}")
    print("-" * 50)
    
    # Query the quota table
    quota_data = query_quota_table()
    
    if quota_data:
        print(f"Found {len(quota_data)} records in quota table:")
        print("-" * 50)
        
        # Print formatted JSON output
        formatted_json = json.dumps(quota_data, indent=2, ensure_ascii=False)
        print(formatted_json)
    else:
        print("No records found in quota table or table does not exist.")

if __name__ == "__main__":
    main()
