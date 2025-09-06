#!/usr/bin/env python3
"""
Manual testing script for the Telegram Communa Bot.

This script allows testing the bot functionality manually with actual Telegram credentials.
Make sure you have set the required environment variables:
- TELEGRAM_BOT_TOKEN
- TARGET_GROUP_ID

Usage:
    python manual_test.py

The script will start the bot and provide instructions for manual testing.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_environment():
    """Check if all required environment variables are set."""
    load_dotenv()
    
    required_vars = ['TELEGRAM_BOT_TOKEN', 'TARGET_GROUP_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        print("See .env.example for reference.")
        return False
    
    print("✅ All required environment variables are set.")
    return True

def print_test_instructions():
    """Print manual testing instructions."""
    print("\n" + "="*60)
    print("MANUAL TESTING INSTRUCTIONS")
    print("="*60)
    print("1. Add your bot to the target group as an administrator")
    print("2. Open a private chat with your bot")
    print("3. Send various message types to test forwarding:")
    print("   - Text messages")
    print("   - Photos")
    print("   - Videos") 
    print("   - Documents")
    print("   - GIFs/Animations")
    print("4. Check that messages appear in the group with [UID:XXXXXXXX] prefix")
    print("5. Reply to bot messages in the group to test reverse forwarding")
    print("6. Check that replies are delivered back to original users")
    print("\nPress Ctrl+C to stop the bot")
    print("="*60)

async def main():
    """Main function to run manual tests."""
    print("🤖 Telegram Communa Bot - Manual Testing")
    
    if not check_environment():
        sys.exit(1)
    
    try:
        from telegram_communa_bot.main import main as bot_main
        print_test_instructions()
        print("\n🚀 Starting bot...")
        bot_main()
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error running bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())