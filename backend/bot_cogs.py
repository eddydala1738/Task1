"""
Discord Bot Cogs for modular functionality
This file contains organized command groups using discord.py Cogs
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from bot_config import bot_config

logger = logging.getLogger(__name__)

class GeneralCog(commands.Cog):
    """General commands and functionality"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot_config
    
    @app_commands.command(name="bot_help", description="Shows available commands and help information")
    async def bot_help_command(self, interaction: discord.Interaction):
        """Help command showing all available commands"""
        logger.info(f"Help command used by {interaction.user}")
        
        embed = discord.Embed(
            title="🤖 Bot Help",
            description="Here are all the available commands and features:",
            color=discord.Color.blue()
        )
        
        # Add slash commands
        slash_commands = self.config.get_slash_commands()
        if slash_commands:
            slash_help = "\n".join([f"`/{cmd}` - {info['description']}" 
                                   for cmd, info in slash_commands.items() 
                                   if info.get('enabled', True)])
            embed.add_field(
                name="📋 Slash Commands",
                value=slash_help,
                inline=False
            )
        
        # Add keyword responses
        keywords = self.config.get_keywords_responses()
        if keywords:
            keyword_help = "\n".join([f"`{keyword}` - Bot responds when this word is mentioned" 
                                     for keyword in keywords.keys()][:5])  # Show first 5
            embed.add_field(
                name="🔍 Keyword Responses",
                value=keyword_help,
                inline=False
            )
        
        embed.add_field(
            name="💡 Tips",
            value="• You can use keywords in any message\n• Slash commands work anywhere\n• Bot responds to mentions",
            inline=False
        )
        
        embed.set_footer(text="Bot is ready to help!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ping", description="Checks if the bot is responding")
    async def ping_command(self, interaction: discord.Interaction):
        """Ping command to check bot responsiveness"""
        logger.info(f"Ping command used by {interaction.user}")
        
        latency = round(self.bot.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot is responding!\nLatency: {latency}ms",
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed)

class NavigationCog(commands.Cog):
    """Navigation and channel-related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot_config
    
    @app_commands.command(name="rules", description="Redirects you to the rules channel")
    async def rules_command(self, interaction: discord.Interaction):
        """Rules command that redirects to rules channel"""
        logger.info(f"Rules command used by {interaction.user}")
        
        channels = self.config.get_channels()
        rules_channel_id = channels.get("rules", "1234567890123456789")
        response = f"📋 Please check out the rules in <#{rules_channel_id}>."
        
        await interaction.response.send_message(response)
    
    @app_commands.command(name="join", description="Shows instructions on how to join roles or channels")
    async def join_command(self, interaction: discord.Interaction):
        """Join command with instructions"""
        logger.info(f"Join command used by {interaction.user}")
        
        channels = self.config.get_channels()
        general_channel = channels.get("general", "1234567890123456789")
        
        embed = discord.Embed(
            title="🚪 How to Join",
            description="Here's how you can join roles and channels:",
            color=discord.Color.green()
        )
        
        embed.add_field(
            name="🎭 Roles",
            value=f"• Use the reaction roles in <#{general_channel}>\n• Contact a moderator for special roles\n• Check the rules first!",
            inline=False
        )
        
        embed.add_field(
            name="📢 Channels",
            value=f"• Most channels are auto-accessible\n• Some require specific roles\n• Ask in <#{general_channel}> for help",
            inline=False
        )
        
        embed.add_field(
            name="❗ Important",
            value="Make sure to read the rules before participating!",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)

class AdminCog(commands.Cog):
    """Admin-only commands for bot management"""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = bot_config
    
    @app_commands.command(name="reload_config", description="Reload bot configuration (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def reload_config(self, interaction: discord.Interaction):
        """Reload bot configuration"""
        logger.info(f"Config reload requested by {interaction.user}")
        
        try:
            self.config.reload_config()
            await interaction.response.send_message("✅ Configuration reloaded successfully!", ephemeral=True)
        except Exception as e:
            logger.error(f"Error reloading config: {e}")
            await interaction.response.send_message(f"❌ Error reloading config: {e}", ephemeral=True)
    
    @app_commands.command(name="admin_info", description="Show bot information (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def admin_info(self, interaction: discord.Interaction):
        """Show bot information"""
        logger.info(f"Bot info requested by {interaction.user}")
        
        embed = discord.Embed(
            title="🤖 Bot Information",
            description="Discord Bot with keyword responses and slash commands",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Guilds", value=str(len(self.bot.guilds)), inline=True)
        embed.add_field(name="Users", value=str(len(self.bot.users)), inline=True)
        embed.add_field(name="Commands", value=str(len(self.bot.tree.get_commands())), inline=True)
        
        keywords_count = len(self.config.get_keywords_responses())
        channels_count = len(self.config.get_channels())
        
        embed.add_field(name="Keywords", value=str(keywords_count), inline=True)
        embed.add_field(name="Channels", value=str(channels_count), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency * 1000)}ms", inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

# Function to add all cogs to the bot
async def setup_cogs(bot):
    """Setup all cogs"""
    await bot.add_cog(GeneralCog(bot))
    await bot.add_cog(NavigationCog(bot))
    await bot.add_cog(AdminCog(bot))
    logger.info("All cogs loaded successfully")