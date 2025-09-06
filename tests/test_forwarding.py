#!/bin/env/python3

import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_uid_generation():
    """Test UID generation and mapping functionality."""
    # Set required environment variables
    os.environ['TELEGRAM_BOT_TOKEN'] = '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
    os.environ['TARGET_GROUP_ID'] = '123456'
    
    from telegram_communa_bot.main import generate_uid, get_user_by_uid, uid_mapping, user_uid_mapping
    
    # Clear mappings for clean test
    uid_mapping.clear()
    user_uid_mapping.clear()
    
    # Test UID generation
    user_id = 12345
    uid = generate_uid(user_id)
    
    assert uid is not None
    assert len(uid) == 8
    assert uid.isupper()
    assert uid_mapping[uid] == user_id
    assert user_uid_mapping[user_id] == uid
    
    # Test same user gets same UID
    uid2 = generate_uid(user_id)
    assert uid == uid2
    
    # Test different user gets different UID
    user_id2 = 67890
    uid3 = generate_uid(user_id2)
    assert uid3 != uid
    assert uid_mapping[uid3] == user_id2


def test_get_user_by_uid():
    """Test retrieving user by UID."""
    # Set required environment variables
    os.environ['TELEGRAM_BOT_TOKEN'] = '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
    os.environ['TARGET_GROUP_ID'] = '123456'
    
    from telegram_communa_bot.main import generate_uid, get_user_by_uid, uid_mapping, user_uid_mapping
    
    # Clear mappings for clean test
    uid_mapping.clear()
    user_uid_mapping.clear()
    
    # Test existing UID
    user_id = 12345
    uid = generate_uid(user_id)
    retrieved_user_id = get_user_by_uid(uid)
    assert retrieved_user_id == user_id
    
    # Test non-existing UID
    non_existing_uid = get_user_by_uid("NONEXIST")
    assert non_existing_uid is None


def test_configuration():
    """Test that configuration functions work correctly."""
    # Test with valid token
    os.environ['TELEGRAM_BOT_TOKEN'] = '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
    from telegram_communa_bot.main import get_token
    assert get_token() == '1234567890:ABCdefGHIjklMNOpqrsTUVwxyz'
    
    # Test with valid group ID
    os.environ['TARGET_GROUP_ID'] = '-100123456789'
    from telegram_communa_bot.main import get_target_group_id
    assert get_target_group_id() == -100123456789


if __name__ == "__main__":
    test_uid_generation()
    test_get_user_by_uid()
    test_configuration()
    print("All forwarding tests passed!")