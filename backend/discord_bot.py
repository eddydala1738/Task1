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
            "join": "To join roles or channels, use `/join` command for instructions!"
        }
        
        self.channels = {
            "rules": "1234567890123456789",  # Replace with actual channel ID
            "general": "1234567890123456789",  # Replace with actual channel ID
            "welcome": "1234567890123456789"  # Replace with actual channel ID
        }
        
        self.slash_commands_help = {
            "/help": "Shows this help message with available commands",
            "/rules": "Redirects you to the rules channel",
            "/join": "Shows instructions on how to join roles or channels",
            "/ping": "Checks if the bot is responding"
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
                name="for messages | /help"
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

# Slash Commands
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
        name="📋 Slash Commands",
        value="\n".join([f"`{cmd}` - {desc}" for cmd, desc in config.slash_commands_help.items()]),
        inline=False
    )
    
    # Add keyword responses
    embed.add_field(
        name="🔍 Keyword Responses",
        value=f"The bot responds to these keywords in messages:\n" +
              "\n".join([f"`{keyword}` - {response}" for keyword, response in config.keywords_responses.items()]),
        inline=False
    )
    
    embed.add_field(
        name="💡 Tips",
        value="• You can use keywords in any message\n• Slash commands work anywhere\n• Bot responds to mentions",
        inline=False
    )
    
    embed.set_footer(text="Bot is ready to help!")
    
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="rules", description="Redirects you to the rules channel")
async def rules_command(interaction: discord.Interaction):
    """Rules command that redirects to rules channel"""
    logger.info(f"Rules command used by {interaction.user}")
    
    rules_channel_id = config.channels["rules"]
    response = f"📋 Please check out the rules in <#{rules_channel_id}>."
    
    await interaction.response.send_message(response)

@bot.tree.command(name="join", description="Shows instructions on how to join roles or channels")
async def join_command(interaction: discord.Interaction):
    """Join command with instructions"""
    logger.info(f"Join command used by {interaction.user}")
    
    embed = discord.Embed(
        title="🚪 How to Join",
        description="Here's how you can join roles and channels:",
        color=discord.Color.green()
    )
    
    embed.add_field(
        name="🎭 Roles",
        value="• Use the reaction roles in <#1234567890123456789>\n• Contact a moderator for special roles\n• Check the rules first!",
        inline=False
    )
    
    embed.add_field(
        name="📢 Channels",
        value="• Most channels are auto-accessible\n• Some require specific roles\n• Ask in <#1234567890123456789> for help",
        inline=False
    )
    
    embed.add_field(
        name="❗ Important",
        value="Make sure to read the rules before participating!",
        inline=False
    )
    
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
    
    await interaction.response.send_message(embed=embed)

# Traditional prefix commands (optional)
@bot.command(name="info")
async def info_command(ctx):
    """Bot info command"""
    embed = discord.Embed(
        title="🤖 Bot Information",
        description="Discord Bot with keyword responses and slash commands",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Guilds", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Users", value=str(len(bot.users)), inline=True)
    embed.add_field(name="Commands", value=str(len(bot.tree.get_commands())), inline=True)
    
    await ctx.send(embed=embed)

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
    
    logger.info("Starting Discord bot...")
    
    try:
        async with bot:
            await bot.start(token)
    except discord.LoginFailure:
        logger.error("Invalid bot token!")
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())