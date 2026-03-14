import sqlite3
import os

DB_PATH = "d:/Project/1/micro_saas_forge/titan_orders.db"

def check_revenue():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Get completed orders
        cursor.execute("SELECT id, original_price, cost_price, proxy_price, profit, create_time FROM orders WHERE status='COMPLETED'")
        rows = cursor.fetchall()
        
        if not rows:
            print("No completed orders found.")
            return

        print(f"Total Completed Orders: {len(rows)}")
        
        prefixes = {}
        for row in rows:
            order_id = row[0]
            prefix = order_id.split('_')[0] if '_' in order_id else "OTHER"
            prefixes[prefix] = prefixes.get(prefix, 0) + 1
            
        print("\nOrder Source Distribution:")
        for prefix, count in prefixes.items():
            print(f"- {prefix}: {count} orders")
            
        # Extract one example of each prefix
        print("\nExamples:")
        for prefix in prefixes:
            cursor.execute(f"SELECT id, profit FROM orders WHERE id LIKE '{prefix}%' AND status='COMPLETED' LIMIT 1")
            example = cursor.fetchone()
            print(f"- {prefix} Example: {example[0]} (Profit: {example[1]})")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_revenue()
