"""
Discord Bot Configuration
This file contains customizable settings for the Discord bot.
"""

import json
from typing import Dict, Any
from pathlib import Path

class BotConfiguration:
    """Configuration manager for the Discord bot"""
    
    def __init__(self, config_file: str = "bot_config.json"):
        self.config_file = Path(__file__).parent / config_file
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading config: {e}")
                return self.default_config()
        else:
            config = self.default_config()
            self.save_config(config)
            return config
    
    def save_config(self, config: Dict[str, Any] = None):
        """Save configuration to JSON file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def default_config(self) -> Dict[str, Any]:
        """Default configuration settings"""
        return {
            "keywords_responses": {
                "help": "Here are the available commands! Use `/help` for more details.",
                "rules": "Please check out the rules in <#1234567890123456789>.",
                "join": "To join roles or channels, use `/join` command for instructions!",
                "welcome": "Welcome to the server! Please read the rules first.",
                "support": "For support, please contact the moderators or use the support channel.",
                "order": "To place an order, use `/place_order` command!",
                "payment": "We accept PayPal payments. Use `/place_order` to start!",
                "status": "Check your order status with `/order_status` or `/my_orders`!"
            },
            "channels": {
                "rules": "1234567890123456789",
                "general": "1391484598604660777",
                "welcome": "1234567890123456789",
                "support": "1234567890123456789",
                "orders": "1234567890123456789"
            },
            "settings": {
                "prefix": "!",
                "case_sensitive": False,
                "respond_to_mentions": True,
                "log_commands": True,
                "max_order_quantity": 100,
                "min_product_name_length": 2
            },
            "slash_commands": {
                "help": {
                    "description": "Shows this help message with available commands",
                    "enabled": True
                },
                "rules": {
                    "description": "Redirects you to the rules channel",
                    "enabled": True
                },
                "join": {
                    "description": "Shows instructions on how to join roles or channels",
                    "enabled": True
                },
                "ping": {
                    "description": "Checks if the bot is responding",
                    "enabled": True
                },
                "place_order": {
                    "description": "Place a new order for products",
                    "enabled": True
                },
                "my_orders": {
                    "description": "View your order history",
                    "enabled": True
                },
                "order_status": {
                    "description": "Check status of a specific order",
                    "enabled": True
                }
            },
            "order_settings": {
                "payment_methods": ["PayPal"],
                "default_payment_method": "PayPal",
                "order_number_format": "ORD-{:03d}",
                "admin_roles": ["admin", "moderator", "mod"],
                "notification_enabled": True,
                "max_orders_per_user": 50
            }
        }
    
    def get_keywords_responses(self) -> Dict[str, str]:
        """Get keyword responses dictionary"""
        return self.config.get("keywords_responses", {})
    
    def get_channels(self) -> Dict[str, str]:
        """Get channels dictionary"""
        return self.config.get("channels", {})
    
    def get_settings(self) -> Dict[str, Any]:
        """Get general settings"""
        return self.config.get("settings", {})
    
    def get_slash_commands(self) -> Dict[str, Dict[str, Any]]:
        """Get slash commands configuration"""
        return self.config.get("slash_commands", {})
    
    def get_order_settings(self) -> Dict[str, Any]:
        """Get order-specific settings"""
        return self.config.get("order_settings", {})
    
    def update_keyword_response(self, keyword: str, response: str):
        """Update a keyword response"""
        self.config["keywords_responses"][keyword] = response
        self.save_config()
    
    def update_channel(self, channel_name: str, channel_id: str):
        """Update a channel ID"""
        self.config["channels"][channel_name] = channel_id
        self.save_config()
    
    def add_keyword_response(self, keyword: str, response: str):
        """Add a new keyword response"""
        self.config["keywords_responses"][keyword] = response
        self.save_config()
    
    def remove_keyword_response(self, keyword: str):
        """Remove a keyword response"""
        if keyword in self.config["keywords_responses"]:
            del self.config["keywords_responses"][keyword]
            self.save_config()
    
    def reload_config(self):
        """Reload configuration from file"""
        self.config = self.load_config()

# Create global configuration instance
bot_config = BotConfiguration()