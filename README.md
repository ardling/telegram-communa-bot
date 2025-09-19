# Telegram communa bot

Telegram bot for message forwarding between private chats and a community group.

## Features

- Forward private messages (text, photo, video, animation, document) to a target
  group with UID markers
- Forward replies from the group back to original users

## Setup

1. Create a bot via [@BotFather](https://t.me/botfather) and get the token
2. Set environment variables:
   ```bash
   export TELEGRAM_BOT_TOKEN=your_bot_token_here
   export BOT_ADMIN=TG_UID
   ```
3. Install dependencies and run:
   ```bash
   pip install -e .
   telegram-communa-bot
   ```

UID:GID `12090`

## Usage

1. Add the bot to your target group
2. `/start`
3. send UID to admin
4. Users send private messages to the bot
5. Messages are forwarded to the group
6. Group members can reply to bot messages to respond to original users

## Development

Run tests:

```bash
pytest tests/
```

Add `.env`

`eval $(poetry env activate)`
