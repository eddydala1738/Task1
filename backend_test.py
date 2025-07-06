#!/usr/bin/env python3
"""
Discord Bot Test Suite
This file tests the Discord bot implementation without connecting to Discord.
"""

import unittest
import os
import sys
import json
import asyncio
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

class DiscordBotTests(unittest.TestCase):
    """Test suite for Discord bot implementation"""

    def setUp(self):
        """Set up test environment"""
        # Ensure we're working with the backend directory
        self.backend_dir = Path(__file__).parent / 'backend'
        os.chdir(self.backend_dir)
        
        # Check if .env file exists
        self.env_file = self.backend_dir / '.env'
        self.assertTrue(self.env_file.exists(), "The .env file is missing")

    def test_bot_token_exists(self):
        """Test if the Discord bot token is properly configured in .env"""
        # Import dotenv here to load environment variables
        from dotenv import load_dotenv
        load_dotenv(self.env_file)
        
        token = os.getenv('DISCORD_BOT_TOKEN')
        self.assertIsNotNone(token, "DISCORD_BOT_TOKEN not found in .env file")
        self.assertTrue(len(token) > 0, "DISCORD_BOT_TOKEN is empty")
        
        # Basic token format validation (Discord tokens are typically long and contain dots)
        self.assertIn(".", token, "Token format appears invalid (should contain dots)")
        self.assertTrue(len(token) > 20, "Token appears too short to be valid")

    def test_dependencies_installed(self):
        """Test if required dependencies are installed"""
        try:
            import discord
            from discord.ext import commands
            from discord import app_commands
            import aiosqlite
            
            # Check discord.py version
            self.assertTrue(discord.__version__ >= "2.3.0", "discord.py version should be at least 2.3.0")
            
            # Check aiosqlite is installed for order database
            self.assertTrue(hasattr(aiosqlite, "connect"), "aiosqlite should have connect method")
            
        except ImportError as e:
            self.fail(f"Required dependency not installed: {e}")

    def test_bot_config_structure(self):
        """Test the bot configuration management system"""
        try:
            from bot_config import BotConfiguration, bot_config
            
            # Test if bot_config is an instance of BotConfiguration
            self.assertIsInstance(bot_config, BotConfiguration, "bot_config should be an instance of BotConfiguration")
            
            # Test configuration methods
            self.assertIsInstance(bot_config.get_keywords_responses(), dict, "get_keywords_responses should return a dictionary")
            self.assertIsInstance(bot_config.get_channels(), dict, "get_channels should return a dictionary")
            self.assertIsInstance(bot_config.get_settings(), dict, "get_settings should return a dictionary")
            self.assertIsInstance(bot_config.get_slash_commands(), dict, "get_slash_commands should return a dictionary")
            
            # Test order settings
            self.assertIsInstance(bot_config.get_order_settings(), dict, "get_order_settings should return a dictionary")
            order_settings = bot_config.get_order_settings()
            self.assertIn("payment_methods", order_settings, "Order settings should contain payment_methods")
            self.assertIn("order_number_format", order_settings, "Order settings should contain order_number_format")
            self.assertIn("admin_roles", order_settings, "Order settings should contain admin_roles")
            
            # Test if default config file is created
            config_file = self.backend_dir / "bot_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                self.assertIn("keywords_responses", config_data, "Config should contain keywords_responses")
                self.assertIn("channels", config_data, "Config should contain channels")
                self.assertIn("settings", config_data, "Config should contain settings")
                self.assertIn("slash_commands", config_data, "Config should contain slash_commands")
                self.assertIn("order_settings", config_data, "Config should contain order_settings")
        except ImportError as e:
            self.fail(f"Failed to import bot_config: {e}")
        except Exception as e:
            self.fail(f"Error testing bot_config: {e}")

    def test_discord_bot_structure(self):
        """Test the Discord bot main file structure"""
        try:
            # Instead of importing and testing objects directly, let's check the file content
            discord_bot_file = self.backend_dir / 'discord_bot.py'
            self.assertTrue(discord_bot_file.exists(), "discord_bot.py should exist")
            
            with open(discord_bot_file, 'r') as f:
                content = f.read()
                
                # Check for key class and function definitions
                self.assertIn('class DiscordBot(commands.Bot):', content, "DiscordBot class should be defined")
                self.assertIn('class BotConfig:', content, "BotConfig class should be defined")
                self.assertIn('bot = DiscordBot()', content, "bot instance should be created")
                self.assertIn('async def main():', content, "main function should be defined")
                
                # Check for key functionality
                self.assertIn('async def on_message', content, "on_message handler should be defined")
                self.assertIn('async def on_ready', content, "on_ready handler should be defined")
                self.assertIn('async def setup_hook', content, "setup_hook should be defined")
                self.assertIn('DISCORD_BOT_TOKEN', content, "Bot should use DISCORD_BOT_TOKEN")
                
                # Check for order system integration
                self.assertIn('from order_manager import order_manager', content, "Order manager should be imported")
                self.assertIn('await order_manager.initialize_db()', content, "Order database should be initialized")
                self.assertIn('from order_cogs import setup_order_cogs', content, "Order cogs should be imported")
                self.assertIn('await setup_order_cogs(self)', content, "Order cogs should be set up")
                
                # Check for order-related keywords
                self.assertIn('"order":', content, "Order keyword should be defined")
                self.assertIn('"payment":', content, "Payment keyword should be defined")
                self.assertIn('"status":', content, "Status keyword should be defined")
                
                # Check for order commands in help
                self.assertIn('Order Commands', content, "Order commands should be in help")
                self.assertIn('place_order', content, "place_order command should be in help")
                self.assertIn('my_orders', content, "my_orders command should be in help")
                self.assertIn('order_status', content, "order_status command should be in help")
                self.assertIn('Admin Commands', content, "Admin commands should be in help")
                self.assertIn('confirm_payment', content, "confirm_payment command should be in help")
                self.assertIn('update_order_status', content, "update_order_status command should be in help")
        except Exception as e:
            self.fail(f"Error testing discord_bot: {e}")

    def test_bot_cogs_structure(self):
        """Test the bot cogs structure"""
        try:
            # Check if the file exists
            bot_cogs_file = self.backend_dir / 'bot_cogs.py'
            self.assertTrue(bot_cogs_file.exists(), "bot_cogs.py should exist")
            
            # Check file content instead of importing
            with open(bot_cogs_file, 'r') as f:
                content = f.read()
                
                # Check for key class definitions
                self.assertIn('class GeneralCog(commands.Cog):', content, "GeneralCog class should be defined")
                self.assertIn('class NavigationCog(commands.Cog):', content, "NavigationCog class should be defined")
                self.assertIn('class AdminCog(commands.Cog):', content, "AdminCog class should be defined")
                
                # Check for setup function
                self.assertIn('async def setup_cogs(bot):', content, "setup_cogs function should be defined")
                
                # Check for key command definitions
                self.assertIn('@app_commands.command(name="help"', content, "help command should be defined")
                self.assertIn('@app_commands.command(name="ping"', content, "ping command should be defined")
                self.assertIn('@app_commands.command(name="rules"', content, "rules command should be defined")
                self.assertIn('@app_commands.command(name="join"', content, "join command should be defined")
        except Exception as e:
            self.fail(f"Error testing bot_cogs: {e}")

    def test_order_cogs_structure(self):
        """Test the order cogs structure"""
        try:
            # Check if the file exists
            order_cogs_file = self.backend_dir / 'order_cogs.py'
            self.assertTrue(order_cogs_file.exists(), "order_cogs.py should exist")
            
            # Check file content
            with open(order_cogs_file, 'r') as f:
                content = f.read()
                
                # Check for key class definitions
                self.assertIn('class OrderCog(commands.Cog):', content, "OrderCog class should be defined")
                self.assertIn('class AdminOrderCog(commands.Cog):', content, "AdminOrderCog class should be defined")
                
                # Check for setup function
                self.assertIn('async def setup_order_cogs(bot):', content, "setup_order_cogs function should be defined")
                
                # Check for user commands
                self.assertIn('@app_commands.command(name="place_order"', content, "place_order command should be defined")
                self.assertIn('@app_commands.command(name="my_orders"', content, "my_orders command should be defined")
                self.assertIn('@app_commands.command(name="order_status"', content, "order_status command should be defined")
                
                # Check for admin commands
                self.assertIn('@app_commands.command(name="confirm_payment"', content, "confirm_payment command should be defined")
                self.assertIn('@app_commands.command(name="update_order_status"', content, "update_order_status command should be defined")
                self.assertIn('@app_commands.command(name="view_orders"', content, "view_orders command should be defined")
                self.assertIn('@app_commands.command(name="search_orders"', content, "search_orders command should be defined")
                self.assertIn('@app_commands.command(name="order_report"', content, "order_report command should be defined")
                
                # Check for admin permission checks
                self.assertIn('def is_admin_or_mod', content, "is_admin_or_mod function should be defined")
                self.assertIn('if not self.is_admin_or_mod', content, "Admin commands should check permissions")
        except Exception as e:
            self.fail(f"Error testing order_cogs: {e}")

    def test_run_bot_script(self):
        """Test the bot launcher script"""
        try:
            # Mock the main function to prevent actual bot startup
            with patch('discord_bot.main'):
                # Mock sys.exit to prevent actual exit
                with patch('sys.exit'):
                    # Import the run_bot module
                    import run_bot
                    
                    # The import should succeed without errors
                    self.assertTrue(True, "run_bot.py imported successfully")
        except ImportError as e:
            self.fail(f"Failed to import run_bot: {e}")
        except Exception as e:
            self.fail(f"Error testing run_bot: {e}")

    def test_bot_command_structure(self):
        """Test the bot command structure"""
        try:
            # Check discord_bot.py for command definitions
            discord_bot_file = self.backend_dir / 'discord_bot.py'
            self.assertTrue(discord_bot_file.exists(), "discord_bot.py should exist")
            
            with open(discord_bot_file, 'r') as f:
                content = f.read()
                self.assertIn('@bot.tree.command(name="help"', content, "help command should be defined")
                self.assertIn('@bot.tree.command(name="ping"', content, "ping command should be defined")
                
            # Check order_cogs.py for order command definitions
            order_cogs_file = self.backend_dir / 'order_cogs.py'
            self.assertTrue(order_cogs_file.exists(), "order_cogs.py should exist")
            
            with open(order_cogs_file, 'r') as f:
                content = f.read()
                self.assertIn('@app_commands.command(name="place_order"', content, "place_order command should be defined")
                self.assertIn('@app_commands.command(name="my_orders"', content, "my_orders command should be defined")
                self.assertIn('@app_commands.command(name="order_status"', content, "order_status command should be defined")
                self.assertIn('@app_commands.command(name="confirm_payment"', content, "confirm_payment command should be defined")
                self.assertIn('@app_commands.command(name="update_order_status"', content, "update_order_status command should be defined")
        except Exception as e:
            self.fail(f"Error testing bot command structure: {e}")

class OrderManagerTests(unittest.TestCase):
    """Test suite for Order Management System"""
    
    def setUp(self):
        """Set up test environment"""
        self.backend_dir = Path(__file__).parent / 'backend'
        os.chdir(self.backend_dir)
        
        # Create a temporary database file for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
        # Patch the OrderManager to use our temporary database
        self.db_path_patcher = patch('order_manager.OrderManager.db_path', Path(self.temp_db.name))
        self.db_path_patcher.start()
        
        # Import order manager after patching
        from order_manager import OrderManager, OrderStatus
        import aiosqlite
        self.OrderManager = OrderManager
        self.OrderStatus = OrderStatus
        self.aiosqlite = aiosqlite
        
        # Create a test instance
        self.order_manager = OrderManager()
    
    def tearDown(self):
        """Clean up after tests"""
        self.db_path_patcher.stop()
        
        # Remove temporary database
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def run_async(self, coro):
        """Helper to run async tests"""
        return asyncio.get_event_loop().run_until_complete(coro)
    
    def test_database_initialization(self):
        """Test database initialization"""
        # Initialize the database
        self.run_async(self.order_manager.initialize_db())
        
        # Check if the database was initialized
        self.assertTrue(self.order_manager.db_initialized, "Database should be initialized")
        
        # Check if the database file exists
        self.assertTrue(os.path.exists(self.temp_db.name), "Database file should exist")
        
        # Check if tables were created by trying to insert and retrieve data
        async def check_tables():
            async with self.aiosqlite.connect(self.temp_db.name) as db:
                # Check orders table
                await db.execute(
                    "INSERT INTO orders (order_number, user_id, username, product_name, quantity, status, created_at, updated_at) "
                    "VALUES ('TEST-001', '123456789', 'TestUser', 'Test Product', 1, 'Pending', '2023-01-01', '2023-01-01')"
                )
                
                # Check order_history table
                await db.execute(
                    "INSERT INTO order_history (order_number, status_from, status_to, changed_by, changed_at, notes) "
                    "VALUES ('TEST-001', 'None', 'Pending', 'TestUser', '2023-01-01', 'Test note')"
                )
                
                await db.commit()
                
                # Verify data was inserted
                cursor = await db.execute("SELECT COUNT(*) FROM orders")
                count = (await cursor.fetchone())[0]
                self.assertEqual(count, 1, "Should have 1 order in the database")
                
                cursor = await db.execute("SELECT COUNT(*) FROM order_history")
                count = (await cursor.fetchone())[0]
                self.assertEqual(count, 1, "Should have 1 history entry in the database")
        
        # Run the async test
        self.run_async(check_tables())
    
    def test_order_number_generation(self):
        """Test order number generation"""
        # Initialize the database
        self.run_async(self.order_manager.initialize_db())
        
        # Generate first order number
        order_number = self.run_async(self.order_manager.generate_order_number())
        self.assertEqual(order_number, "ORD-001", "First order number should be ORD-001")
        
        # Create an order to increment the counter
        self.run_async(self.order_manager.create_order("123", "TestUser", "Test Product", 1))
        
        # Generate second order number
        order_number = self.run_async(self.order_manager.generate_order_number())
        self.assertEqual(order_number, "ORD-002", "Second order number should be ORD-002")
    
    def test_create_order(self):
        """Test order creation"""
        # Initialize the database
        self.run_async(self.order_manager.initialize_db())
        
        # Create an order
        order = self.run_async(self.order_manager.create_order(
            user_id="123456789",
            username="TestUser",
            product_name="Test Product",
            quantity=2
        ))
        
        # Check order data
        self.assertEqual(order["order_number"], "ORD-001", "Order number should be ORD-001")
        self.assertEqual(order["user_id"], "123456789", "User ID should match")
        self.assertEqual(order["username"], "TestUser", "Username should match")
        self.assertEqual(order["product_name"], "Test Product", "Product name should match")
        self.assertEqual(order["quantity"], 2, "Quantity should match")
        self.assertEqual(order["status"], "Pending", "Status should be Pending")
        self.assertEqual(order["payment_method"], "PayPal", "Payment method should be PayPal")
        
        # Retrieve the order to verify it was saved
        retrieved_order = self.run_async(self.order_manager.get_order("ORD-001"))
        self.assertIsNotNone(retrieved_order, "Order should be retrievable")
        self.assertEqual(retrieved_order["order_number"], "ORD-001", "Retrieved order number should match")
        self.assertEqual(retrieved_order["status"], "Pending", "Retrieved status should be Pending")
    
    def test_update_order_status(self):
        """Test order status updates"""
        # Initialize the database
        self.run_async(self.order_manager.initialize_db())
        
        # Create an order
        self.run_async(self.order_manager.create_order(
            user_id="123456789",
            username="TestUser",
            product_name="Test Product",
            quantity=1
        ))
        
        # Update status to Paid
        success = self.run_async(self.order_manager.update_order_status(
            order_number="ORD-001",
            new_status=self.OrderStatus.PAID,
            changed_by="AdminUser",
            notes="Payment received"
        ))
        
        self.assertTrue(success, "Status update should succeed")
        
        # Verify status was updated
        order = self.run_async(self.order_manager.get_order("ORD-001"))
        self.assertEqual(order["status"], "Paid", "Status should be updated to Paid")
        self.assertEqual(order["confirmed_by"], "AdminUser", "Confirmed by should be set")
        self.assertEqual(order["notes"], "Payment received", "Notes should be set")
        
        # Check order history
        history = self.run_async(self.order_manager.get_order_history("ORD-001"))
        self.assertEqual(len(history), 2, "Should have 2 history entries")
        self.assertEqual(history[0]["status_from"], "Pending", "First status change should be from Pending")
        self.assertEqual(history[0]["status_to"], "Paid", "First status change should be to Paid")
        
        # Update to next status
        success = self.run_async(self.order_manager.update_order_status(
            order_number="ORD-001",
            new_status=self.OrderStatus.PROCESSING,
            changed_by="AdminUser",
            notes="Order processing started"
        ))
        
        self.assertTrue(success, "Second status update should succeed")
        
        # Verify status was updated again
        order = self.run_async(self.order_manager.get_order("ORD-001"))
        self.assertEqual(order["status"], "Processing", "Status should be updated to Processing")
        
        # Check order history again
        history = self.run_async(self.order_manager.get_order_history("ORD-001"))
        self.assertEqual(len(history), 3, "Should have 3 history entries")
        self.assertEqual(history[0]["status_from"], "Paid", "Second status change should be from Paid")
        self.assertEqual(history[0]["status_to"], "Processing", "Second status change should be to Processing")
    
    def test_get_user_orders(self):
        """Test retrieving user orders"""
        # Initialize the database
        self.run_async(self.order_manager.initialize_db())
        
        # Create multiple orders for the same user
        self.run_async(self.order_manager.create_order(
            user_id="123456789",
            username="TestUser",
            product_name="Product A",
            quantity=1
        ))
        
        self.run_async(self.order_manager.create_order(
            user_id="123456789",
            username="TestUser",
            product_name="Product B",
            quantity=2
        ))
        
        # Create an order for a different user
        self.run_async(self.order_manager.create_order(
            user_id="987654321",
            username="OtherUser",
            product_name="Product C",
            quantity=3
        ))
        
        # Get orders for the first user
        user_orders = self.run_async(self.order_manager.get_user_orders("123456789"))
        
        # Check results
        self.assertEqual(len(user_orders), 2, "Should have 2 orders for the user")
        self.assertEqual(user_orders[0]["product_name"], "Product B", "First order should be Product B (most recent)")
        self.assertEqual(user_orders[1]["product_name"], "Product A", "Second order should be Product A")
        
        # Get orders for the second user
        other_user_orders = self.run_async(self.order_manager.get_user_orders("987654321"))
        
        # Check results
        self.assertEqual(len(other_user_orders), 1, "Should have 1 order for the other user")
        self.assertEqual(other_user_orders[0]["product_name"], "Product C", "Order should be Product C")
    
    def test_search_orders(self):
        """Test searching orders"""
        # Initialize the database
        self.run_async(self.order_manager.initialize_db())
        
        # Create test orders
        self.run_async(self.order_manager.create_order(
            user_id="123456789",
            username="TestUser",
            product_name="Gaming Mouse",
            quantity=1
        ))
        
        self.run_async(self.order_manager.create_order(
            user_id="987654321",
            username="JohnDoe",
            product_name="Gaming Keyboard",
            quantity=1
        ))
        
        self.run_async(self.order_manager.create_order(
            user_id="555555555",
            username="JaneSmith",
            product_name="Gaming Headset",
            quantity=1
        ))
        
        # Update status of one order
        self.run_async(self.order_manager.update_order_status(
            order_number="ORD-002",
            new_status=self.OrderStatus.PAID,
            changed_by="AdminUser"
        ))
        
        # Search by product name
        results = self.run_async(self.order_manager.search_orders(query="Gaming"))
        self.assertEqual(len(results), 3, "Should find all 3 gaming products")
        
        # Search by specific product
        results = self.run_async(self.order_manager.search_orders(query="Mouse"))
        self.assertEqual(len(results), 1, "Should find only the mouse product")
        self.assertEqual(results[0]["product_name"], "Gaming Mouse", "Should find the mouse product")
        
        # Search by username
        results = self.run_async(self.order_manager.search_orders(query="John"))
        self.assertEqual(len(results), 1, "Should find only JohnDoe's order")
        self.assertEqual(results[0]["username"], "JohnDoe", "Should find JohnDoe's order")
        
        # Search by status
        results = self.run_async(self.order_manager.search_orders(status="Paid"))
        self.assertEqual(len(results), 1, "Should find only the paid order")
        self.assertEqual(results[0]["order_number"], "ORD-002", "Should find order ORD-002")
        
        # Search by status and query
        results = self.run_async(self.order_manager.search_orders(query="Gaming", status="Pending"))
        self.assertEqual(len(results), 2, "Should find 2 pending gaming products")
    
    def test_get_order_stats(self):
        """Test order statistics"""
        # Initialize the database
        self.run_async(self.order_manager.initialize_db())
        
        # Create test orders
        self.run_async(self.order_manager.create_order(
            user_id="123456789",
            username="TestUser",
            product_name="Product A",
            quantity=1
        ))
        
        self.run_async(self.order_manager.create_order(
            user_id="987654321",
            username="OtherUser",
            product_name="Product B",
            quantity=2
        ))
        
        # Update status of one order
        self.run_async(self.order_manager.update_order_status(
            order_number="ORD-001",
            new_status=self.OrderStatus.PAID,
            changed_by="AdminUser"
        ))
        
        # Get stats
        stats = self.run_async(self.order_manager.get_order_stats())
        
        # Check results
        self.assertEqual(stats["total_orders"], 2, "Should have 2 total orders")
        self.assertEqual(stats["status_counts"]["Pending"], 1, "Should have 1 pending order")
        self.assertEqual(stats["status_counts"]["Paid"], 1, "Should have 1 paid order")
        self.assertEqual(stats["recent_orders"], 2, "Should have 2 recent orders")

class OrderCogsTests(unittest.TestCase):
    """Test suite for Order Cogs"""
    
    def setUp(self):
        """Set up test environment"""
        self.backend_dir = Path(__file__).parent / 'backend'
        os.chdir(self.backend_dir)
        
        # Import necessary modules
        from order_cogs import OrderCog, AdminOrderCog
        from order_manager import OrderManager, OrderStatus
        
        # Mock the bot
        self.bot = MagicMock()
        
        # Mock the order manager
        self.order_manager = MagicMock(spec=OrderManager)
        
        # Create a patch for the global order_manager in order_cogs
        self.order_manager_patcher = patch('order_cogs.order_manager', self.order_manager)
        self.order_manager_patcher.start()
        
        # Create cog instances
        self.order_cog = OrderCog(self.bot)
        self.admin_order_cog = AdminOrderCog(self.bot)
        
        # Store OrderStatus for testing
        self.OrderStatus = OrderStatus
    
    def tearDown(self):
        """Clean up after tests"""
        self.order_manager_patcher.stop()
    
    def test_order_cog_initialization(self):
        """Test OrderCog initialization"""
        self.assertEqual(self.order_cog.bot, self.bot, "Bot should be set correctly")
        self.assertEqual(self.order_cog.order_manager, self.order_manager, "Order manager should be set correctly")
    
    def test_admin_order_cog_initialization(self):
        """Test AdminOrderCog initialization"""
        self.assertEqual(self.admin_order_cog.bot, self.bot, "Bot should be set correctly")
        self.assertEqual(self.admin_order_cog.order_manager, self.order_manager, "Order manager should be set correctly")
    
    def test_admin_permission_check(self):
        """Test admin permission check"""
        # Create mock users with different roles
        admin_user = MagicMock()
        admin_user.roles = [MagicMock(name="admin")]
        
        mod_user = MagicMock()
        mod_user.roles = [MagicMock(name="moderator")]
        
        regular_user = MagicMock()
        regular_user.roles = [MagicMock(name="member")]
        
        # Test permission checks
        self.assertTrue(self.admin_order_cog.is_admin_or_mod(admin_user), "Admin user should have permission")
        self.assertTrue(self.admin_order_cog.is_admin_or_mod(mod_user), "Moderator user should have permission")
        self.assertFalse(self.admin_order_cog.is_admin_or_mod(regular_user), "Regular user should not have permission")
    
    def test_place_order_command_validation(self):
        """Test place_order command validation"""
        # Create mock interaction
        interaction = AsyncMock()
        interaction.user.id = 123456789
        interaction.user.display_name = "TestUser"
        
        # Test with invalid quantity
        asyncio.run(self.order_cog.place_order(interaction, "Test Product", 0))
        interaction.response.send_message.assert_called_with("❌ Quantity must be a positive number!", ephemeral=True)
        
        # Reset mock
        interaction.response.send_message.reset_mock()
        
        # Test with too large quantity
        asyncio.run(self.order_cog.place_order(interaction, "Test Product", 101))
        interaction.response.send_message.assert_called_with("❌ Quantity cannot exceed 100 items per order!", ephemeral=True)
        
        # Reset mock
        interaction.response.send_message.reset_mock()
        
        # Test with invalid product name
        asyncio.run(self.order_cog.place_order(interaction, " ", 1))
        interaction.response.send_message.assert_called_with("❌ Product name must be at least 2 characters!", ephemeral=True)
    
    def test_place_order_command_success(self):
        """Test successful place_order command"""
        # Create mock interaction
        interaction = AsyncMock()
        interaction.user.id = 123456789
        interaction.user.display_name = "TestUser"
        
        # Mock order_manager.create_order to return a sample order
        sample_order = {
            "order_number": "ORD-001",
            "user_id": "123456789",
            "username": "TestUser",
            "product_name": "Test Product",
            "quantity": 1,
            "status": "Pending",
            "created_at": "2023-01-01T12:00:00",
            "payment_method": "PayPal"
        }
        self.order_manager.create_order = AsyncMock(return_value=sample_order)
        
        # Call the command
        asyncio.run(self.order_cog.place_order(interaction, "Test Product", 1))
        
        # Verify order_manager.create_order was called with correct parameters
        self.order_manager.create_order.assert_called_with(
            user_id="123456789",
            username="TestUser",
            product_name="Test Product",
            quantity=1
        )
        
        # Verify response was sent
        interaction.response.send_message.assert_called_once()
        
        # Check that the embed was created (we can't easily check the content)
        args, kwargs = interaction.response.send_message.call_args
        self.assertIn("embed", kwargs)
    
    def test_confirm_payment_command(self):
        """Test confirm_payment command"""
        # Create mock interaction with admin user
        interaction = AsyncMock()
        interaction.user.id = 123456789
        interaction.user.display_name = "AdminUser"
        interaction.user.roles = [MagicMock(name="admin")]
        
        # Mock order_manager.get_order to return a sample order
        sample_order = {
            "order_number": "ORD-001",
            "user_id": "987654321",
            "username": "CustomerUser",
            "product_name": "Test Product",
            "quantity": 1,
            "status": "Pending",
            "created_at": "2023-01-01T12:00:00",
            "payment_method": "PayPal"
        }
        self.order_manager.get_order = AsyncMock(return_value=sample_order)
        
        # Mock order_manager.update_order_status to return success
        self.order_manager.update_order_status = AsyncMock(return_value=True)
        
        # Mock bot.fetch_user to return a user
        self.bot.fetch_user = AsyncMock(return_value=MagicMock())
        
        # Call the command
        asyncio.run(self.admin_order_cog.confirm_payment(interaction, "ORD-001", "Payment received via PayPal"))
        
        # Verify order_manager.get_order was called with correct parameters
        self.order_manager.get_order.assert_called_with("ORD-001")
        
        # Verify order_manager.update_order_status was called with correct parameters
        self.order_manager.update_order_status.assert_called_with(
            "ORD-001",
            self.OrderStatus.PAID,
            "AdminUser",
            "Payment received via PayPal"
        )
        
        # Verify response was sent
        interaction.response.send_message.assert_called_once()
        
        # Check that the confirmation message was sent
        args, kwargs = interaction.response.send_message.call_args
        self.assertIn("✅ Payment confirmed for order ORD-001", args[0])
    
    def test_update_order_status_command(self):
        """Test update_order_status command"""
        # Create mock interaction with admin user
        interaction = AsyncMock()
        interaction.user.id = 123456789
        interaction.user.display_name = "AdminUser"
        interaction.user.roles = [MagicMock(name="admin")]
        
        # Mock order_manager.get_order to return a sample order
        sample_order = {
            "order_number": "ORD-001",
            "user_id": "987654321",
            "username": "CustomerUser",
            "product_name": "Test Product",
            "quantity": 1,
            "status": "Paid",
            "created_at": "2023-01-01T12:00:00",
            "payment_method": "PayPal"
        }
        self.order_manager.get_order = AsyncMock(return_value=sample_order)
        
        # Mock order_manager.update_order_status to return success
        self.order_manager.update_order_status = AsyncMock(return_value=True)
        
        # Mock bot.fetch_user to return a user
        self.bot.fetch_user = AsyncMock(return_value=MagicMock())
        
        # Call the command
        asyncio.run(self.admin_order_cog.update_order_status(interaction, "ORD-001", "Processing", "Order processing started"))
        
        # Verify order_manager.get_order was called with correct parameters
        self.order_manager.get_order.assert_called_with("ORD-001")
        
        # Verify order_manager.update_order_status was called with correct parameters
        self.order_manager.update_order_status.assert_called_with(
            "ORD-001",
            self.OrderStatus.PROCESSING,
            "AdminUser",
            "Order processing started"
        )
        
        # Verify response was sent
        interaction.response.send_message.assert_called_once()
        
        # Check that the confirmation message was sent
        args, kwargs = interaction.response.send_message.call_args
        self.assertIn("✅ Order ORD-001 status updated to Processing", args[0])

if __name__ == '__main__':
    unittest.main()
