"""
Order Management Cogs for Discord Bot
Contains order-related commands and functionality
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from typing import Optional
from order_manager import order_manager, OrderStatus
from datetime import datetime

logger = logging.getLogger(__name__)

class OrderCog(commands.Cog):
    """Order management commands for regular users"""
    
    def __init__(self, bot):
        self.bot = bot
        self.order_manager = order_manager
    
    @app_commands.command(name="place_order", description="Place a new order")
    @app_commands.describe(
        product_name="Name of the product you want to order",
        quantity="Quantity of the product (must be positive)"
    )
    async def place_order(self, interaction: discord.Interaction, product_name: str, quantity: int):
        """Place a new order"""
        logger.info(f"Order placement attempt by {interaction.user}")
        
        # Validate quantity
        if quantity <= 0:
            await interaction.response.send_message("❌ Quantity must be a positive number!", ephemeral=True)
            return
        
        if quantity > 100:
            await interaction.response.send_message("❌ Quantity cannot exceed 100 items per order!", ephemeral=True)
            return
        
        # Validate product name
        if len(product_name.strip()) < 2:
            await interaction.response.send_message("❌ Product name must be at least 2 characters!", ephemeral=True)
            return
        
        try:
            # Create order
            order = await self.order_manager.create_order(
                user_id=str(interaction.user.id),
                username=interaction.user.display_name,
                product_name=product_name.strip(),
                quantity=quantity
            )
            
            # Create order confirmation embed
            embed = discord.Embed(
                title="🛍️ Order Placed Successfully!",
                description=f"Your order has been created and is waiting for payment confirmation.",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Order Number", value=f"`{order['order_number']}`", inline=True)
            embed.add_field(name="Product", value=product_name, inline=True)
            embed.add_field(name="Quantity", value=str(quantity), inline=True)
            embed.add_field(name="Status", value="🟡 Pending Payment", inline=True)
            embed.add_field(name="Payment Method", value="PayPal", inline=True)
            embed.add_field(name="Created", value=f"<t:{int(datetime.fromisoformat(order['created_at'].replace('Z', '+00:00')).timestamp())}:R>", inline=True)
            
            embed.add_field(
                name="📋 Next Steps", 
                value="1. Make payment via PayPal\n2. Wait for admin/moderator to confirm payment\n3. Your order will be processed", 
                inline=False
            )
            
            embed.set_footer(text=f"Order ID: {order['order_number']} | Use /my_orders to track your orders")
            
            await interaction.response.send_message(embed=embed)
            
            # Log order creation
            logger.info(f"Order {order['order_number']} created by {interaction.user.display_name}")
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            await interaction.response.send_message("❌ An error occurred while placing your order. Please try again.", ephemeral=True)
    
    @app_commands.command(name="my_orders", description="View your orders")
    async def my_orders(self, interaction: discord.Interaction):
        """View user's orders"""
        logger.info(f"Order lookup by {interaction.user}")
        
        try:
            orders = await self.order_manager.get_user_orders(str(interaction.user.id))
            
            if not orders:
                embed = discord.Embed(
                    title="📦 Your Orders",
                    description="You haven't placed any orders yet.",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Get Started", value="Use `/place_order` to place your first order!", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            # Create orders embed
            embed = discord.Embed(
                title="📦 Your Orders",
                description=f"You have {len(orders)} order(s)",
                color=discord.Color.blue()
            )
            
            for order in orders[:5]:  # Show last 5 orders
                status_emoji = {
                    "Pending": "🟡",
                    "Paid": "🟢",
                    "Processing": "🔄",
                    "Completed": "✅",
                    "Cancelled": "❌"
                }.get(order["status"], "⚪")
                
                embed.add_field(
                    name=f"{order['order_number']} - {order['product_name']}",
                    value=f"Status: {status_emoji} {order['status']}\nQuantity: {order['quantity']}\nCreated: <t:{int(datetime.fromisoformat(order['created_at']).timestamp())}:R>",
                    inline=True
                )
            
            if len(orders) > 5:
                embed.add_field(
                    name="📋 More Orders", 
                    value=f"Showing 5 of {len(orders)} orders. Use `/order_status` to check specific orders.", 
                    inline=False
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error retrieving orders: {e}")
            await interaction.response.send_message("❌ An error occurred while retrieving your orders.", ephemeral=True)
    
    @app_commands.command(name="order_status", description="Check the status of a specific order")
    @app_commands.describe(order_number="Order number (e.g., ORD-001)")
    async def order_status(self, interaction: discord.Interaction, order_number: str):
        """Check order status"""
        logger.info(f"Order status check for {order_number} by {interaction.user}")
        
        try:
            order = await self.order_manager.get_order(order_number.upper())
            
            if not order:
                await interaction.response.send_message("❌ Order not found! Please check the order number.", ephemeral=True)
                return
            
            # Check if user owns this order or is admin
            if order["user_id"] != str(interaction.user.id):
                # Check if user has admin/moderator permissions
                if not any(role.name.lower() in ['admin', 'moderator', 'mod'] for role in interaction.user.roles):
                    await interaction.response.send_message("❌ You can only view your own orders!", ephemeral=True)
                    return
            
            # Get order history
            history = await self.order_manager.get_order_history(order_number.upper())
            
            status_emoji = {
                "Pending": "🟡",
                "Paid": "🟢",
                "Processing": "🔄",
                "Completed": "✅",
                "Cancelled": "❌"
            }.get(order["status"], "⚪")
            
            embed = discord.Embed(
                title=f"📋 Order Details - {order['order_number']}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="Product", value=order["product_name"], inline=True)
            embed.add_field(name="Quantity", value=str(order["quantity"]), inline=True)
            embed.add_field(name="Status", value=f"{status_emoji} {order['status']}", inline=True)
            embed.add_field(name="Customer", value=order["username"], inline=True)
            embed.add_field(name="Payment Method", value=order["payment_method"], inline=True)
            embed.add_field(name="Created", value=f"<t:{int(datetime.fromisoformat(order['created_at']).timestamp())}:R>", inline=True)
            
            if order["confirmed_by"]:
                embed.add_field(name="Confirmed By", value=order["confirmed_by"], inline=True)
            
            if order["notes"]:
                embed.add_field(name="Notes", value=order["notes"], inline=False)
            
            # Add status history
            if history:
                history_text = ""
                for h in history[:3]:  # Show last 3 status changes
                    timestamp = int(datetime.fromisoformat(h["changed_at"]).timestamp())
                    history_text += f"• {h['status_from']} → {h['status_to']} by {h['changed_by']} <t:{timestamp}:R>\n"
                
                embed.add_field(name="📈 Recent History", value=history_text, inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error checking order status: {e}")
            await interaction.response.send_message("❌ An error occurred while checking the order status.", ephemeral=True)

class AdminOrderCog(commands.Cog):
    """Admin-only order management commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.order_manager = order_manager
    
    def is_admin_or_mod(self, user: discord.Member) -> bool:
        """Check if user has admin or moderator permissions"""
        return any(role.name.lower() in ['admin', 'moderator', 'mod'] for role in user.roles)
    
    @app_commands.command(name="confirm_payment", description="Confirm payment for an order (Admin/Mod only)")
    @app_commands.describe(
        order_number="Order number (e.g., ORD-001)",
        notes="Optional notes about the payment confirmation"
    )
    async def confirm_payment(self, interaction: discord.Interaction, order_number: str, notes: Optional[str] = None):
        """Confirm payment for an order"""
        if not self.is_admin_or_mod(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
            return
        
        logger.info(f"Payment confirmation attempt for {order_number} by {interaction.user}")
        
        try:
            order = await self.order_manager.get_order(order_number.upper())
            
            if not order:
                await interaction.response.send_message("❌ Order not found!", ephemeral=True)
                return
            
            if order["status"] != "Pending":
                await interaction.response.send_message(f"❌ Order is already {order['status']}. Can only confirm payment for pending orders.", ephemeral=True)
                return
            
            # Update order status to Paid
            success = await self.order_manager.update_order_status(
                order_number.upper(),
                OrderStatus.PAID,
                interaction.user.display_name,
                notes or "Payment confirmed by admin"
            )
            
            if success:
                # Notify user
                try:
                    user = await self.bot.fetch_user(int(order["user_id"]))
                    if user:
                        embed = discord.Embed(
                            title="✅ Payment Confirmed!",
                            description=f"Your payment for order {order['order_number']} has been confirmed!",
                            color=discord.Color.green()
                        )
                        embed.add_field(name="Order Number", value=order["order_number"], inline=True)
                        embed.add_field(name="Product", value=order["product_name"], inline=True)
                        embed.add_field(name="Quantity", value=str(order["quantity"]), inline=True)
                        embed.add_field(name="Status", value="🟢 Paid", inline=True)
                        embed.add_field(name="Confirmed By", value=interaction.user.display_name, inline=True)
                        
                        if notes:
                            embed.add_field(name="Notes", value=notes, inline=False)
                        
                        embed.add_field(name="Next Steps", value="Your order is now paid and will be processed soon!", inline=False)
                        
                        await user.send(embed=embed)
                except Exception as e:
                    logger.warning(f"Could not notify user about payment confirmation: {e}")
                
                # Confirmation message
                await interaction.response.send_message(f"✅ Payment confirmed for order {order['order_number']}! User has been notified.", ephemeral=True)
                
            else:
                await interaction.response.send_message("❌ Failed to confirm payment. Please try again.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            await interaction.response.send_message("❌ An error occurred while confirming payment.", ephemeral=True)
    
    @app_commands.command(name="update_order_status", description="Update order status (Admin/Mod only)")
    @app_commands.describe(
        order_number="Order number (e.g., ORD-001)",
        status="New status for the order",
        notes="Optional notes about the status change"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="Pending", value="Pending"),
        app_commands.Choice(name="Paid", value="Paid"),
        app_commands.Choice(name="Processing", value="Processing"),
        app_commands.Choice(name="Completed", value="Completed"),
        app_commands.Choice(name="Cancelled", value="Cancelled")
    ])
    async def update_order_status(self, interaction: discord.Interaction, order_number: str, status: str, notes: Optional[str] = None):
        """Update order status"""
        if not self.is_admin_or_mod(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
            return
        
        logger.info(f"Status update attempt for {order_number} to {status} by {interaction.user}")
        
        try:
            order = await self.order_manager.get_order(order_number.upper())
            
            if not order:
                await interaction.response.send_message("❌ Order not found!", ephemeral=True)
                return
            
            if order["status"] == status:
                await interaction.response.send_message(f"❌ Order is already {status}!", ephemeral=True)
                return
            
            # Update order status
            success = await self.order_manager.update_order_status(
                order_number.upper(),
                OrderStatus(status),
                interaction.user.display_name,
                notes or f"Status updated to {status}"
            )
            
            if success:
                # Notify user
                try:
                    user = await self.bot.fetch_user(int(order["user_id"]))
                    if user:
                        status_emoji = {
                            "Pending": "🟡",
                            "Paid": "🟢",
                            "Processing": "🔄",
                            "Completed": "✅",
                            "Cancelled": "❌"
                        }.get(status, "⚪")
                        
                        embed = discord.Embed(
                            title="📋 Order Status Updated",
                            description=f"Your order {order['order_number']} status has been updated!",
                            color=discord.Color.blue()
                        )
                        embed.add_field(name="Order Number", value=order["order_number"], inline=True)
                        embed.add_field(name="Product", value=order["product_name"], inline=True)
                        embed.add_field(name="New Status", value=f"{status_emoji} {status}", inline=True)
                        embed.add_field(name="Updated By", value=interaction.user.display_name, inline=True)
                        
                        if notes:
                            embed.add_field(name="Notes", value=notes, inline=False)
                        
                        await user.send(embed=embed)
                except Exception as e:
                    logger.warning(f"Could not notify user about status update: {e}")
                
                # Confirmation message
                await interaction.response.send_message(f"✅ Order {order['order_number']} status updated to {status}! User has been notified.", ephemeral=True)
                
            else:
                await interaction.response.send_message("❌ Failed to update order status. Please try again.", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
            await interaction.response.send_message("❌ An error occurred while updating the order status.", ephemeral=True)
    
    @app_commands.command(name="view_orders", description="View all orders (Admin/Mod only)")
    @app_commands.describe(
        status="Filter by status (optional)",
        limit="Number of orders to show (default: 10)"
    )
    @app_commands.choices(status=[
        app_commands.Choice(name="All", value="all"),
        app_commands.Choice(name="Pending", value="Pending"),
        app_commands.Choice(name="Paid", value="Paid"),
        app_commands.Choice(name="Processing", value="Processing"),
        app_commands.Choice(name="Completed", value="Completed"),
        app_commands.Choice(name="Cancelled", value="Cancelled")
    ])
    async def view_orders(self, interaction: discord.Interaction, status: Optional[str] = "all", limit: Optional[int] = 10):
        """View all orders"""
        if not self.is_admin_or_mod(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
            return
        
        logger.info(f"Order view request by {interaction.user} with status filter: {status}")
        
        try:
            status_filter = None if status == "all" else status
            orders = await self.order_manager.search_orders(status=status_filter, limit=min(limit, 25))
            
            if not orders:
                embed = discord.Embed(
                    title="📦 Orders",
                    description="No orders found matching your criteria.",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title="📦 Orders Management",
                description=f"Showing {len(orders)} order(s)" + (f" with status: {status}" if status != "all" else ""),
                color=discord.Color.blue()
            )
            
            for order in orders:
                status_emoji = {
                    "Pending": "🟡",
                    "Paid": "🟢",
                    "Processing": "🔄",
                    "Completed": "✅",
                    "Cancelled": "❌"
                }.get(order["status"], "⚪")
                
                embed.add_field(
                    name=f"{order['order_number']} - {order['username']}",
                    value=f"Product: {order['product_name']}\nQty: {order['quantity']}\nStatus: {status_emoji} {order['status']}\nCreated: <t:{int(datetime.fromisoformat(order['created_at']).timestamp())}:R>",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error viewing orders: {e}")
            await interaction.response.send_message("❌ An error occurred while retrieving orders.", ephemeral=True)
    
    @app_commands.command(name="search_orders", description="Search orders (Admin/Mod only)")
    @app_commands.describe(query="Search term (order number, username, or product name)")
    async def search_orders(self, interaction: discord.Interaction, query: str):
        """Search orders"""
        if not self.is_admin_or_mod(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
            return
        
        logger.info(f"Order search by {interaction.user} with query: {query}")
        
        try:
            orders = await self.order_manager.search_orders(query=query, limit=15)
            
            if not orders:
                embed = discord.Embed(
                    title="🔍 Search Results",
                    description=f"No orders found matching '{query}'.",
                    color=discord.Color.blue()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🔍 Search Results",
                description=f"Found {len(orders)} order(s) matching '{query}'",
                color=discord.Color.blue()
            )
            
            for order in orders:
                status_emoji = {
                    "Pending": "🟡",
                    "Paid": "🟢",
                    "Processing": "🔄",
                    "Completed": "✅",
                    "Cancelled": "❌"
                }.get(order["status"], "⚪")
                
                embed.add_field(
                    name=f"{order['order_number']} - {order['username']}",
                    value=f"Product: {order['product_name']}\nQty: {order['quantity']}\nStatus: {status_emoji} {order['status']}\nCreated: <t:{int(datetime.fromisoformat(order['created_at']).timestamp())}:R>",
                    inline=True
                )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error searching orders: {e}")
            await interaction.response.send_message("❌ An error occurred while searching orders.", ephemeral=True)
    
    @app_commands.command(name="order_report", description="Generate order statistics report (Admin/Mod only)")
    async def order_report(self, interaction: discord.Interaction):
        """Generate order statistics report"""
        if not self.is_admin_or_mod(interaction.user):
            await interaction.response.send_message("❌ You don't have permission to use this command!", ephemeral=True)
            return
        
        logger.info(f"Order report requested by {interaction.user}")
        
        try:
            stats = await self.order_manager.get_order_stats()
            
            embed = discord.Embed(
                title="📊 Order Statistics Report",
                description="Complete overview of all orders",
                color=discord.Color.gold()
            )
            
            embed.add_field(name="Total Orders", value=str(stats["total_orders"]), inline=True)
            embed.add_field(name="Recent Orders (7 days)", value=str(stats["recent_orders"]), inline=True)
            embed.add_field(name="", value="", inline=True)  # Empty field for spacing
            
            # Status breakdown
            status_counts = stats["status_counts"]
            status_text = ""
            for status, count in status_counts.items():
                status_emoji = {
                    "Pending": "🟡",
                    "Paid": "🟢",
                    "Processing": "🔄",
                    "Completed": "✅",
                    "Cancelled": "❌"
                }.get(status, "⚪")
                status_text += f"{status_emoji} {status}: {count}\n"
            
            embed.add_field(name="📋 Orders by Status", value=status_text or "No orders yet", inline=False)
            
            embed.set_footer(text=f"Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error generating order report: {e}")
            await interaction.response.send_message("❌ An error occurred while generating the report.", ephemeral=True)

# Function to add all order cogs to the bot
async def setup_order_cogs(bot):
    """Setup all order cogs"""
    await bot.add_cog(OrderCog(bot))
    await bot.add_cog(AdminOrderCog(bot))
    logger.info("Order cogs loaded successfully")