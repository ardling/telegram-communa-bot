#!/bin/env/python3

"""
Integration tests for message forwarding functionality.
These tests simulate the message flow without requiring actual Telegram API calls.
"""

import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch

from src.telegram_communa_bot.main import (
    forward_to_group,
    uid_mapping,
    user_uid_mapping,
    generate_uid,
    handle_group_reply,
)


def setup_test_environment():
    """Setup test environment with required variables."""
    os.environ["TELEGRAM_BOT_TOKEN"] = "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
    os.environ["TARGET_GROUP_ID"] = "123456"


@pytest.mark.asyncio
async def test_private_message_forwarding_flow():
    """Test the complete flow of forwarding a private message to group."""
    setup_test_environment()

    # Clear mappings for clean test
    uid_mapping.clear()
    user_uid_mapping.clear()

    # Mock message object
    mock_message = MagicMock()
    mock_message.text = "Hello, this is a test message"
    mock_message.photo = None
    mock_message.video = None
    mock_message.animation = None
    mock_message.document = None
    mock_message.answer = AsyncMock()

    # Mock bot
    with patch("telegram_communa_bot.main.bot") as mock_bot:
        mock_bot.send_message = AsyncMock()

        # Test message forwarding
        user_id = 12345
        uid = "TESTUID1"

        await forward_to_group(mock_message, user_id, uid)

        # Verify bot.send_message was called with correct parameters
        mock_bot.send_message.assert_called_once_with(
            123456, "[UID:TESTUID1] Hello, this is a test message"  # TARGET_GROUP_ID
        )

        # Verify user received confirmation
        mock_message.answer.assert_called_once_with("Сообщение отправлено в группу.")


@pytest.mark.asyncio
async def test_group_reply_forwarding_flow():
    """Test the complete flow of forwarding a group reply back to user."""
    setup_test_environment()

    # Clear mappings and setup test UID
    uid_mapping.clear()
    user_uid_mapping.clear()
    user_id = 12345
    uid = generate_uid(user_id)

    # Mock reply message in group
    mock_reply_message = MagicMock()
    mock_reply_message.text = "[UID:{}] Hello, this is a test message".format(uid)
    mock_reply_message.caption = None
    mock_reply_message.from_user.id = 999999999  # Bot ID (different from user)

    # Mock the group message (reply)
    mock_message = MagicMock()
    mock_message.text = "This is a reply from group"
    mock_message.reply_to_message = mock_reply_message

    # Mock bot
    with patch("telegram_communa_bot.main.bot") as mock_bot:
        mock_bot.id = 999999999  # Same as reply_message.from_user.id
        mock_bot.send_message = AsyncMock()

        await handle_group_reply(mock_message)

        # Verify bot.send_message was called to forward reply back to user
        mock_bot.send_message.assert_called_once_with(
            user_id, "Ответ из группы: This is a reply from group"
        )


@pytest.mark.asyncio
async def test_unsupported_message_type():
    """Test handling of unsupported message types."""
    setup_test_environment()

    # Mock message with unsupported type (no text, photo, video, animation, document)
    mock_message = MagicMock()
    mock_message.text = None
    mock_message.photo = None
    mock_message.video = None
    mock_message.animation = None
    mock_message.document = None
    mock_message.answer = AsyncMock()

    with patch("telegram_communa_bot.main.bot") as mock_bot:
        mock_bot.send_message = AsyncMock()

        await forward_to_group(mock_message, 12345, "TESTUID")

        # Verify bot did NOT send message to group
        mock_bot.send_message.assert_not_called()

        # Verify user received error message
        mock_message.answer.assert_called_once_with(
            "Извините, этот тип сообщения не поддерживается."
        )


if __name__ == "__main__":
    import asyncio

    async def run_tests():
        await test_private_message_forwarding_flow()
        await test_group_reply_forwarding_flow()
        await test_unsupported_message_type()
        print("All integration tests passed!")

    asyncio.run(run_tests())
