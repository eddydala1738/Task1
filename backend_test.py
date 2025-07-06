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
from pathlib import Path
from unittest.mock import patch, MagicMock

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
            self.assertEqual(discord.__version__, "2.5.2", "discord.py version should be 2.5.2")
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
            
            # Test if default config file is created
            config_file = self.backend_dir / "bot_config.json"
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                self.assertIn("keywords_responses", config_data, "Config should contain keywords_responses")
                self.assertIn("channels", config_data, "Config should contain channels")
                self.assertIn("settings", config_data, "Config should contain settings")
                self.assertIn("slash_commands", config_data, "Config should contain slash_commands")
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
                self.assertIn('@bot.tree.command(name="rules"', content, "rules command should be defined")
                self.assertIn('@bot.tree.command(name="join"', content, "join command should be defined")
                self.assertIn('@bot.tree.command(name="ping"', content, "ping command should be defined")
                
            # Also check bot_cogs.py for command definitions
            bot_cogs_file = self.backend_dir / 'bot_cogs.py'
            self.assertTrue(bot_cogs_file.exists(), "bot_cogs.py should exist")
            
            with open(bot_cogs_file, 'r') as f:
                content = f.read()
                self.assertIn('@app_commands.command(name="help"', content, "help command should be defined in cogs")
                self.assertIn('@app_commands.command(name="rules"', content, "rules command should be defined in cogs")
                self.assertIn('@app_commands.command(name="join"', content, "join command should be defined in cogs")
                self.assertIn('@app_commands.command(name="ping"', content, "ping command should be defined in cogs")
        except Exception as e:
            self.fail(f"Error testing bot command structure: {e}")

if __name__ == '__main__':
    unittest.main()