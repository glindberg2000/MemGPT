# chatbot_factory.py

import uuid
from main_api import MemGPTChatbot


def create_chatbot(chatbot_uuid=None):
    if chatbot_uuid == None:
        chatbot_uuid = uuid.uuid4()

    return MemGPTChatbot(chatbot_uuid)
