import uuid
from unittest import mock
from main_api import MemGPTChatbot
from chatbot_factory import create_chatbot


def test_create_chatbot_new_user():
    # Call factory
    chatbot = create_chatbot()

    # Check chatbot instance
    assert isinstance(chatbot, MemGPTChatbot)
    assert isinstance(chatbot.chatbot_uuid, uuid.UUID)


def test_existing_user():
    # Mock UUID
    mock_uuid = uuid.uuid4()

    # Call factory
    chatbot = create_chatbot(mock_uuid)

    # Check chatbot instance
    assert isinstance(chatbot, MemGPTChatbot)
    assert chatbot.chatbot_uuid == mock_uuid


# @mock.patch("main_api.MemGPTChatbot.load_user_config")
# def test_create_chatbot_loads_config(mock_load):
#     # Call factory
#     test_uuid = "d350ea5d-4d2c-4cca-bb74-4311b37143a5"
#     create_chatbot(test_uuid)

#     # Check load user config was called
#     mock_load.assert_called_once_with(test_uuid)
