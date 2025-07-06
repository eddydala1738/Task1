#!/usr/bin/env python3
"""
Order System Demo Script
Quick test of the order management system without Discord
"""

import asyncio
import sys
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from order_manager import OrderManager, OrderStatus

async def demo_order_system():
    """Demonstrate the order management system"""
    print("🛍️ Discord Bot Order Management System Demo")
    print("=" * 50)
    
    # Create order manager with a demo database
    order_mgr = OrderManager("demo_orders.db")
    
    try:
        # Initialize database
        await order_mgr.initialize_db()
        print("✅ Database initialized")
        
        # Create a sample order
        print("\n📝 Creating sample order...")
        order = await order_mgr.create_order(
            user_id="123456789",
            username="TestUser",
            product_name="Discord Bot License",
            quantity=1
        )
        print(f"✅ Order created: {order['order_number']}")
        print(f"   Product: {order['product_name']}")
        print(f"   Quantity: {order['quantity']}")
        print(f"   Status: {order['status']}")
        
        # Simulate payment confirmation
        print(f"\n💳 Confirming payment for {order['order_number']}...")
        success = await order_mgr.update_order_status(
            order['order_number'],
            OrderStatus.PAID,
            "AdminUser",
            "PayPal payment confirmed"
        )
        print(f"✅ Payment confirmed: {success}")
        
        # Update to processing
        print(f"\n⚙️ Processing order {order['order_number']}...")
        success = await order_mgr.update_order_status(
            order['order_number'],
            OrderStatus.PROCESSING,
            "AdminUser",
            "Order is being processed"
        )
        print(f"✅ Status updated to Processing: {success}")
        
        # Complete the order
        print(f"\n🎉 Completing order {order['order_number']}...")
        success = await order_mgr.update_order_status(
            order['order_number'],
            OrderStatus.COMPLETED,
            "AdminUser",
            "Order completed successfully"
        )
        print(f"✅ Order completed: {success}")
        
        # Get order details
        print(f"\n📋 Final order details:")
        final_order = await order_mgr.get_order(order['order_number'])
        print(f"   Order Number: {final_order['order_number']}")
        print(f"   Product: {final_order['product_name']}")
        print(f"   Status: {final_order['status']}")
        print(f"   Confirmed By: {final_order['confirmed_by']}")
        
        # Get order history
        print(f"\n📈 Order history:")
        history = await order_mgr.get_order_history(order['order_number'])
        for entry in history:
            print(f"   {entry['status_from']} → {entry['status_to']} by {entry['changed_by']}")
        
        # Get statistics
        print(f"\n📊 Order statistics:")
        stats = await order_mgr.get_order_stats()
        print(f"   Total Orders: {stats['total_orders']}")
        print(f"   Status Breakdown: {stats['status_counts']}")
        
        print("\n🎉 Demo completed successfully!")
        print("The order management system is working correctly.")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting order system demo...\n")
    
    try:
        result = asyncio.run(demo_order_system())
        
        if result:
            print("\n✅ All systems working correctly!")
            print("The Discord bot is ready to handle orders.")
        else:
            print("\n❌ Demo failed - check the error messages above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        sys.exit(1)