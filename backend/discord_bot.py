import discord
from discord.ext import commands
from discord import app_commands
import os
import logging
from dotenv import load_dotenv
from pathlib import Path
import json
from typing import Dict, Any
import asyncio

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration
class BotConfig:
    def __init__(self):
        self.keywords_responses = {
            "help": "Here are the available commands! Use `/help` for more details.",
            "rules": "Please check out the rules in <#1234567890123456789>.",
            "join": "To join roles or channels, use `/join` command for instructions!",
            "order": "To place an order, use `/place_order` command!",
            "payment": "We accept PayPal payments. Use `/place_order` to start!",
            "status": "Check your order status with `/order_status` or `/my_orders`!"
        }
        
        self.channels = {
            "rules": "1234567890123456789",  # Replace with actual channel ID
            "general": "1234567890123456789",  # Replace with actual channel ID
            "welcome": "1234567890123456789",  # Replace with actual channel ID
            "orders": "1234567890123456789"   # Replace with actual channel ID
        }
        
        self.slash_commands_help = {
            "/help": "Shows this help message with available commands",
            "/rules": "Redirects you to the rules channel",
            "/join": "Shows instructions on how to join roles or channels",
            "/ping": "Checks if the bot is responding",
            "/place_order": "Place a new order for products",
            "/my_orders": "View your order history",
            "/order_status": "Check status of a specific order"
        }

config = BotConfig()

# Bot setup with intents
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None  # We'll create our own help command
        )
    
    async def setup_hook(self):
        """This is called when the bot is starting up"""
        logger.info(f"Bot is starting up...")
        
        # Initialize order manager
        try:
            from order_manager import order_manager
            await order_manager.initialize_db()
            logger.info("Order database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize order database: {e}")
        
        # Load cogs
        try:
            from bot_cogs import setup_cogs
            await setup_cogs(self)
            logger.info("Basic cogs loaded")
        except Exception as e:
            logger.error(f"Failed to load basic cogs: {e}")
        
        try:
            from order_cogs import setup_order_cogs
            await setup_order_cogs(self)
            logger.info("Order cogs loaded")
        except Exception as e:
            logger.error(f"Failed to load order cogs: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash commands")
        except Exception as e:
            logger.error(f"Failed to sync slash commands: {e}")
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for orders & messages | /help"
            )
        )
    
    async def on_message(self, message):
        """Handle incoming messages"""
        # Don't respond to bot messages
        if message.author.bot:
            return
        
        # Check for keywords in message content
        message_content = message.content.lower()
        
        for keyword, response in config.keywords_responses.items():
            if keyword in message_content:
                logger.info(f"Keyword '{keyword}' detected in message from {message.author}")
                await message.channel.send(response)
                break
        
        # Process commands
        await self.process_commands(message)
    
    async def on_command_error(self, ctx, error):
        """Handle command errors"""
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Command not found! Use `/help` to see available commands.")
        else:
            logger.error(f"Command error: {error}")
            await ctx.send("An error occurred while processing the command.")

# Create bot instance
bot = DiscordBot()

# Basic slash commands (additional ones are in cogs)
@bot.tree.command(name="help", description="Shows available commands and help information")
async def help_command(interaction: discord.Interaction):
    """Help command showing all available commands"""
    logger.info(f"Help command used by {interaction.user}")
    
    embed = discord.Embed(
        title="🤖 Bot Help",
        description="Here are all the available commands and features:",
        color=discord.Color.blue()
    )
    
    # Add slash commands
    embed.add_field(
        name="📋 General Commands",
        value="`/help` - Shows this help message\n`/rules` - View server rules\n`/join` - Join instructions\n`/ping` - Check bot response",
        inline=False
    )
    
    embed.add_field(
        name="🛍️ Order Commands",
        value="`/place_order` - Place a new order\n`/my_orders` - View your orders\n`/order_status` - Check order status",
        inline=False
    )
    
    embed.add_field(
        name="👑 Admin Commands",
        value="`/confirm_payment` - Confirm payment\n`/update_order_status` - Update order status\n`/view_orders` - View all orders\n`/search_orders` - Search orders\n`/order_report` - Generate reports",
        inline=False
    )
    
    # Add keyword responses
    embed.add_field(
        name="🔍 Keyword Responses",
        value="The bot responds to these keywords: `help`, `rules`, `join`, `order`, `payment`, `status`",
        inline=False
    )
    
    embed.add_field(
        name="💡 Order Process",
        value="1. Use `/place_order` to create order\n2. Make PayPal payment\n3. Admin confirms payment\n4. Order gets processed",
        inline=False
    )
    
    embed.set_footer(text="Need help? Contact an admin or moderator!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Checks if the bot is responding")
async def ping_command(interaction: discord.Interaction):
    """Ping command to check bot responsiveness"""
    logger.info(f"Ping command used by {interaction.user}")
    
    latency = round(bot.latency * 1000)
    
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot is responding!\nLatency: {latency}ms",
        color=discord.Color.green()
    )
    
    embed.add_field(name="🛍️ Order System", value="✅ Online", inline=True)
    embed.add_field(name="📋 Commands", value="✅ Active", inline=True)
    
    await interaction.response.send_message(embed=embed)

# Error handling for slash commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle slash command errors"""
    logger.error(f"Slash command error: {error}")
    
    if not interaction.response.is_done():
        await interaction.response.send_message(
            "An error occurred while processing the command. Please try again.",
            ephemeral=True
        )

# Main function to run the bot
async def main():
    """Main function to start the bot"""
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        logger.error("DISCORD_BOT_TOKEN not found in environment variables!")
        return
    
    logger.info("Starting Discord bot with order management system...")
    
    try:
        async with bot:
            await bot.start(token)
    except discord.LoginFailure:
        logger.error("Invalid bot token!")
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())