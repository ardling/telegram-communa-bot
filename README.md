# Telegram communa bot

Telegram bot for message forwarding between private chats and a community group.

## Features

- Forward private messages (text, photo, video, animation, document) to a target group with UID markers
- Forward replies from the group back to original users
- In-memory UID mapping (resets on restart)
- Error handling for unsupported message types

## Setup

1. Create a bot via [@BotFather](https://t.me/botfather) and get the token
2. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN=your_bot_token_here
   export TARGET_GROUP_ID=your_group_chat_id_here
   ```
3. Install dependencies and run:
   ```bash
   pip install -e .
   telegram-communa-bot
   ```

## Usage

1. Add the bot to your target group as an admin
2. Users send private messages to the bot
3. Messages are forwarded to the group with `[UID:XXXXXXXX]` markers
4. Group members can reply to bot messages to respond to original users

## Development

Run tests:
```bash
pytest tests/
```
