"""
Order Management System for Discord Bot
Handles order creation, tracking, and management
"""

import aiosqlite
import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Optional, Any
from pathlib import Path
from enum import Enum

logger = logging.getLogger(__name__)

class OrderStatus(Enum):
    PENDING = "Pending"
    PAID = "Paid"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class OrderManager:
    def __init__(self, db_path: str = "orders.db"):
        self.db_path = Path(__file__).parent / db_path
        self.db_initialized = False
    
    async def initialize_db(self):
        """Initialize the database with required tables"""
        if self.db_initialized:
            return
            
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    username TEXT NOT NULL,
                    product_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    payment_method TEXT DEFAULT 'PayPal',
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    confirmed_by TEXT,
                    notes TEXT
                )
            """)
            
            await db.execute("""
                CREATE TABLE IF NOT EXISTS order_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_number TEXT NOT NULL,
                    status_from TEXT NOT NULL,
                    status_to TEXT NOT NULL,
                    changed_by TEXT NOT NULL,
                    changed_at TIMESTAMP NOT NULL,
                    notes TEXT
                )
            """)
            
            await db.commit()
            logger.info("Database initialized successfully")
            self.db_initialized = True
    
    async def generate_order_number(self) -> str:
        """Generate next order number in format ORD-001"""
        await self.initialize_db()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT MAX(id) FROM orders")
            result = await cursor.fetchone()
            next_id = (result[0] or 0) + 1
            return f"ORD-{next_id:03d}"
    
    async def create_order(self, user_id: str, username: str, product_name: str, quantity: int) -> Dict[str, Any]:
        """Create a new order"""
        await self.initialize_db()
        
        order_number = await self.generate_order_number()
        now = datetime.now(timezone.utc)
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO orders (order_number, user_id, username, product_name, quantity, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_number, user_id, username, product_name, quantity, OrderStatus.PENDING.value, now, now))
            
            # Add to history
            await db.execute("""
                INSERT INTO order_history (order_number, status_from, status_to, changed_by, changed_at, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (order_number, "None", OrderStatus.PENDING.value, username, now, "Order created"))
            
            await db.commit()
            
            logger.info(f"Created order {order_number} for user {username}")
            
            return {
                "order_number": order_number,
                "user_id": user_id,
                "username": username,
                "product_name": product_name,
                "quantity": quantity,
                "status": OrderStatus.PENDING.value,
                "created_at": now.isoformat(),
                "payment_method": "PayPal"
            }
    
    async def get_order(self, order_number: str) -> Optional[Dict[str, Any]]:
        """Get order details by order number"""
        await self.initialize_db()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT order_number, user_id, username, product_name, quantity, status, payment_method, 
                       created_at, updated_at, confirmed_by, notes
                FROM orders WHERE order_number = ?
            """, (order_number,))
            
            row = await cursor.fetchone()
            if not row:
                return None
            
            return {
                "order_number": row[0],
                "user_id": row[1],
                "username": row[2],
                "product_name": row[3],
                "quantity": row[4],
                "status": row[5],
                "payment_method": row[6],
                "created_at": row[7],
                "updated_at": row[8],
                "confirmed_by": row[9],
                "notes": row[10]
            }
    
    async def get_user_orders(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a specific user"""
        await self.initialize_db()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT order_number, user_id, username, product_name, quantity, status, payment_method, 
                       created_at, updated_at, confirmed_by, notes
                FROM orders WHERE user_id = ? ORDER BY created_at DESC
            """, (user_id,))
            
            rows = await cursor.fetchall()
            return [
                {
                    "order_number": row[0],
                    "user_id": row[1],
                    "username": row[2],
                    "product_name": row[3],
                    "quantity": row[4],
                    "status": row[5],
                    "payment_method": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                    "confirmed_by": row[9],
                    "notes": row[10]
                }
                for row in rows
            ]
    
    async def update_order_status(self, order_number: str, new_status: OrderStatus, changed_by: str, notes: str = None) -> bool:
        """Update order status"""
        await self.initialize_db()
        
        # Get current order
        current_order = await self.get_order(order_number)
        if not current_order:
            return False
        
        old_status = current_order["status"]
        now = datetime.now(timezone.utc)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Update order
            await db.execute("""
                UPDATE orders 
                SET status = ?, updated_at = ?, confirmed_by = ?, notes = ?
                WHERE order_number = ?
            """, (new_status.value, now, changed_by, notes, order_number))
            
            # Add to history
            await db.execute("""
                INSERT INTO order_history (order_number, status_from, status_to, changed_by, changed_at, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (order_number, old_status, new_status.value, changed_by, now, notes or f"Status changed to {new_status.value}"))
            
            await db.commit()
            
            logger.info(f"Updated order {order_number} from {old_status} to {new_status.value} by {changed_by}")
            return True
    
    async def search_orders(self, query: str = None, status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Search orders with optional filters"""
        await self.initialize_db()
        
        sql = """
            SELECT order_number, user_id, username, product_name, quantity, status, payment_method, 
                   created_at, updated_at, confirmed_by, notes
            FROM orders WHERE 1=1
        """
        params = []
        
        if query:
            sql += " AND (order_number LIKE ? OR username LIKE ? OR product_name LIKE ?)"
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        if status:
            sql += " AND status = ?"
            params.append(status)
        
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(sql, params)
            rows = await cursor.fetchall()
            
            return [
                {
                    "order_number": row[0],
                    "user_id": row[1],
                    "username": row[2],
                    "product_name": row[3],
                    "quantity": row[4],
                    "status": row[5],
                    "payment_method": row[6],
                    "created_at": row[7],
                    "updated_at": row[8],
                    "confirmed_by": row[9],
                    "notes": row[10]
                }
                for row in rows
            ]
    
    async def get_order_history(self, order_number: str) -> List[Dict[str, Any]]:
        """Get order status history"""
        await self.initialize_db()
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT status_from, status_to, changed_by, changed_at, notes
                FROM order_history WHERE order_number = ? ORDER BY changed_at DESC
            """, (order_number,))
            
            rows = await cursor.fetchall()
            return [
                {
                    "status_from": row[0],
                    "status_to": row[1],
                    "changed_by": row[2],
                    "changed_at": row[3],
                    "notes": row[4]
                }
                for row in rows
            ]
    
    async def get_order_stats(self) -> Dict[str, Any]:
        """Get order statistics for reports"""
        await self.initialize_db()
        
        async with aiosqlite.connect(self.db_path) as db:
            # Total orders
            cursor = await db.execute("SELECT COUNT(*) FROM orders")
            total_orders = (await cursor.fetchone())[0]
            
            # Orders by status
            cursor = await db.execute("SELECT status, COUNT(*) FROM orders GROUP BY status")
            status_counts = {row[0]: row[1] for row in await cursor.fetchall()}
            
            # Recent orders (last 7 days)
            cursor = await db.execute("""
                SELECT COUNT(*) FROM orders 
                WHERE created_at >= datetime('now', '-7 days')
            """)
            recent_orders = (await cursor.fetchone())[0]
            
            return {
                "total_orders": total_orders,
                "status_counts": status_counts,
                "recent_orders": recent_orders
            }

# Global order manager instance
order_manager = OrderManager()