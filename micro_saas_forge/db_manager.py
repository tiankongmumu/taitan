import sqlite3
from loguru import logger
import time
from datetime import datetime, timedelta

class DBManager:
    """商业版专属: 本地 SQLite 订单与财务管理"""
    def __init__(self, db_path="titan_orders.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                target_url TEXT,
                original_price REAL,
                cost_price REAL,
                proxy_price REAL,
                status TEXT, -- PENDING_PAY, PROCESSING, COMPLETED, FAILED, DLQ
                profit REAL,
                create_time INTEGER
            )
        ''')
        
        # [NEW] 100x Optimization: Dead Letter Queue (死信队列)用于存储因缺货/API宕机而失败的补发扣款单
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dlq_orders (
                id TEXT PRIMARY KEY,
                retry_count INTEGER DEFAULT 0,
                last_error TEXT,
                next_retry_at INTEGER,
                FOREIGN KEY(id) REFERENCES orders(id)
            )
        ''')
        conn.commit()
        conn.close()

    def create_order(self, order_id, target_url, orig, cost, proxy, status="PENDING"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (id, target_url, original_price, cost_price, proxy_price, status, profit, create_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, target_url, orig, cost, proxy, status, 0.0, int(time.time())))
        conn.commit()
        conn.close()
        logger.info(f"💾 [DB] 订单已入库: {order_id}")

    def update_status(self, order_id, status):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 如果订单成功完成，计算利润
        if status == "COMPLETED":
            cursor.execute('''
                UPDATE orders SET status = ?, profit = (proxy_price - cost_price)
                WHERE id = ?
            ''', (status, order_id))
        else:
            cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
            
        conn.commit()
        conn.close()

    def get_daily_revenue(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 获取今天的利润总和
        today_start = int(time.time()) - (int(time.time()) % 86400) # 简单取整天的起始时间
        cursor.execute('SELECT SUM(profit), COUNT(id) FROM orders WHERE status = "COMPLETED" AND create_time >= ?', (today_start,))
        row = cursor.fetchone()
        conn.close()
        return {"revenue": row[0] or 0.0, "orders": row[1] or 0}

    # ==========================================
    # [NEW] 100x Optimization: DLQ Methods (容灾防漏单)
    # ==========================================
    def move_to_dlq(self, order_id, error_reason="Unknown Error"):
        """将失败订单移入死信队列，进入重试循环"""
        self.update_status(order_id, "DLQ")
        next_retry_time = int(time.time()) + 300 # 5分钟后重试
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO dlq_orders (id, retry_count, last_error, next_retry_at)
                VALUES (?, 0, ?, ?)
                ON CONFLICT(id) DO UPDATE SET 
                retry_count = retry_count + 1,
                last_error = ?,
                next_retry_at = ?
            ''', (order_id, error_reason, next_retry_time, error_reason, next_retry_time + 900))
            conn.commit()
            logger.warning(f"🚨 警报: 订单 {order_id} 已被打入死信队列 (DLQ)，原因: {error_reason}")
        except Exception as e:
            logger.error(f"DLQ 写入失败: {e}")
        finally:
            conn.close()

    def get_pending_dlq_orders(self):
        """拉取当前需要执行重试的丢单"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT d.id, o.proxy_price, o.cost_price, d.retry_count
            FROM dlq_orders d
            JOIN orders o ON d.id = o.id
            WHERE d.next_retry_at <= ? AND d.retry_count < 5 AND o.status = 'DLQ'
        ''', (int(time.time()),))
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for r in rows:
            results.append({
                "task_id": r[0],
                "proxy_price": r[1],
                "cost_price": r[2],
                "retry_count": r[3]
            })
        return results

if __name__ == "__main__":
    db = DBManager()
    print("Database initialized.")
