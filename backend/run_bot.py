#!/usr/bin/env python3
"""
Discord Bot Runner
Simple script to run the Discord bot with proper setup
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from discord_bot import main

if __name__ == "__main__":
    print("🤖 Starting Discord Bot...")
    print("=" * 50)
    
    # Check if token is present
    token = os.getenv('DISCORD_BOT_TOKEN')
    if not token:
        print("❌ Error: DISCORD_BOT_TOKEN not found in environment variables!")
        print("Please make sure the bot token is set in the .env file")
        sys.exit(1)
    
    print("✅ Bot token found")
    print("🚀 Launching bot...")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        sys.exit(1)