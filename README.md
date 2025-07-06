# Discord Bot

A Python Discord bot using discord.py 2.0+ with keyword responses and slash commands.

## Features

🔧 **Basic Requirements:**
- ✅ Responds to messages with specific keywords (help, rules, join)
- ✅ Replies support channel mentions using `<#channel_id>`
- ✅ Redirects users to channels when keywords are detected
- ✅ Supports slash commands using discord.app_commands
- ✅ Customizable keyword/command system using configuration files

⚙️ **Technical Details:**
- ✅ Uses discord.py 2.0+ for slash commands
- ✅ Bot token setup via .env file using python-dotenv
- ✅ Logs bot events to console
- ✅ Modular structure using Cogs
- ✅ Configuration management system

## Available Commands

### Slash Commands
- `/help` - Shows list of available commands and help info
- `/rules` - Redirects user to the rules channel
- `/join` - Shows instructions on how to join roles or channels
- `/ping` - Confirms the bot is working

### Keyword Responses
The bot automatically responds to these keywords in messages:
- `help` - Shows available commands
- `rules` - Redirects to rules channel
- `join` - Shows join instructions
- `welcome` - Welcome message
- `support` - Support information

## Setup Instructions

1. **Install Dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Bot Token:**
   - The bot token is already set in `backend/.env` file
   - Token: `MTM5MTUwMTQxMzQ2ODg2NDU1Mg.GdiJ6t.iyAtQ68apP5zx6wIi2BadjtpuZpFxJ2ZMfHPDg`

3. **Customize Configuration:**
   - Edit `backend/bot_config.py` to modify responses and channel IDs
   - The bot will create `bot_config.json` for runtime configuration

4. **Run the Bot:**
   ```bash
   cd backend
   python run_bot.py
   ```
   
   Or directly:
   ```bash
   cd backend
   python discord_bot.py
   ```

## File Structure

```
backend/
├── discord_bot.py      # Main bot file
├── bot_config.py       # Configuration management
├── bot_cogs.py         # Modular command groups
├── run_bot.py          # Bot launcher script
├── requirements.txt    # Dependencies
└── .env               # Environment variables
```

## Configuration

### Customizing Responses
Edit the `backend/bot_config.py` file to modify:
- Keyword responses
- Channel IDs
- Slash command settings
- Bot behavior settings

### Adding New Keywords
1. Open `backend/bot_config.py`
2. Add new keyword-response pairs to the `keywords_responses` dictionary
3. Restart the bot

### Updating Channel IDs
1. Replace the placeholder channel IDs in `backend/bot_config.py`
2. Use actual Discord channel IDs from your server
3. Restart the bot

## Bot Permissions

The bot requires these permissions in your Discord server:
- Read Messages
- Send Messages
- Use Slash Commands
- Embed Links
- Read Message History

## Logging

The bot logs all events to the console including:
- Bot startup and connection
- Command usage
- Keyword detections
- Errors and warnings

## Advanced Features

### Modular Design
- Uses Discord.py Cogs for organized command groups
- Separate modules for different functionalities
- Easy to extend and maintain

### Admin Commands
- `/reload_config` - Reload configuration without restart
- `/bot_info` - Show bot statistics and information

### Error Handling
- Graceful error handling for commands
- Logging of all errors
- User-friendly error messages

## Testing the Bot

1. **Start the bot**: `cd backend && python run_bot.py`
2. **Test keyword responses**: Send messages containing "help", "rules", "join"
3. **Test slash commands**: Use `/help`, `/rules`, `/join`, `/ping`
4. **Check logs**: Monitor console for bot activity

## Troubleshooting

### Common Issues:
1. **Bot not responding**: Check if token is valid and bot is online
2. **Slash commands not working**: Ensure bot has proper permissions
3. **Keyword responses not working**: Check if message content intent is enabled

### Bot Token Issues:
- Make sure the token in `.env` is correct
- Check if the bot is added to your Discord server
- Verify bot permissions in Discord Developer Portal

## Next Steps

1. **Add Bot to Server**: Use Discord Developer Portal to add bot to your server
2. **Set Channel IDs**: Replace placeholder IDs with actual channel IDs
3. **Test All Features**: Verify all commands and responses work correctly
4. **Customize Further**: Add more keywords, commands, or features as needed

The bot is ready to use with the provided token and configuration!