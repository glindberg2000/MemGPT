import asyncio
from absl import app, flags
import logging
import os
import sys
import pickle
import uuid

# original imports:
# import memgpt.agent as agent
# import memgpt.system as system
# import memgpt.utils as utils
# import memgpt.presets as presets
# import memgpt.constants as constants
# import memgpt.personas.personas as personas
# import memgpt.humans.humans as humans
# from memgpt.persistence_manager import InMemoryStateManager
# import interface

# Fast API needs absolute imports, so we need to do this:
import fastapi_app.MemGPT.memgpt.agent as agent
import fastapi_app.MemGPT.memgpt.system as system
import fastapi_app.MemGPT.memgpt.utils as utils
import fastapi_app.MemGPT.memgpt.presets as presets
import fastapi_app.MemGPT.memgpt.constants as constants
import fastapi_app.MemGPT.memgpt.personas.personas as personas
import fastapi_app.MemGPT.memgpt.humans.humans as humans
from fastapi_app.MemGPT.memgpt.persistence_manager import InMemoryStateManager
import fastapi_app.MemGPT.interface as interface

# Define flags globally
FLAGS = flags.FLAGS
flags.DEFINE_boolean("debug", False, "Print debug statements")

SAVE_DIR = "saved_state"


class MemGPTChatbot:
    def __init__(
        self,
        chatbot_uuid=uuid.uuid4(),
        user_config=None,
        initial_messages=None,
        debug=False,
    ):
        """
        Initialize chatbot instance.

        Args:
            uuid (str): Unique ID for this chatbot instance
            initial_messages (list): List of initial messages to start conversation
            debug (bool): Whether to print debug statements
        """
        self.chatbot_uuid = chatbot_uuid or str(uuid4())
        self.config = user_config or self.load_user_config(self.chatbot_uuid)
        self.initial_messages = initial_messages or []
        self.debug = debug
        # Create MemGPT agent
        self.memgpt_agent = self._create_memgpt_agent()

        # Message history
        self.messages = []

        # Add initial messages
        if self.initial_messages:
            self.messages.extend(self.initial_messages)

    def load_user_config(self, uuid):
        pass
        # Load config by uuid

    def save_user_config(self, user_config):
        pass
        # Save config by uuid

    def _create_memgpt_agent(self):
        """
        Initialize the MemGPT agent with desired settings.
        """

        # Set up flags and logging
        flags.FLAGS.debug = self.debug
        logging.getLogger().setLevel(logging.DEBUG if self.debug else logging.CRITICAL)

        # Create persistence manager
        persistence_manager = InMemoryStateManager()

        # Create MemGPT agent
        return presets.use_preset(
            presets.DEFAULT,
            constants.DEFAULT_MEMGPT_MODEL,
            personas.DEFAULT,
            humans.DEFAULT,
            interface,  #  printing
            persistence_manager,
        )

    async def chat(self, messages):
        """
        Conduct a conversation with the provided messages.

        Args:
            messages (list): Messages to send to MemGPT agent

        Returns:
            responses (list): MemGPT agent responses
        """

        self.messages.extend(messages)
        responses = []

        for msg in messages:
            packaged_msg = system.package_user_message(msg)
            agent_responses, *_ = await self.memgpt_agent.step(packaged_msg)

            responses.append(agent_responses[-1])
            self.messages.extend(agent_responses)

        # Check if a new assistant message has been received
        if interface.new_message_received:
            latest_message = interface.latest_message
            interface.new_message_received = False  # Reset the flag
        else:
            latest_message = None

        return latest_message

    def save(self, filename):
        # Create saved state dir if needed
        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        # Build full paths
        save_path = os.path.join(SAVE_DIR, filename)
        pm_path = save_path.replace(".json", ".persistence.pickle")

        # Save files
        self.memgpt_agent.save_to_json_file(save_path)
        self.memgpt_agent.persistence_manager.save(pm_path)

        print(f"Saved conversation to {save_path}")
        print(f"Saved persistence manager to {pm_path}")

    def load(self, filename):
        # Build full paths
        load_path = os.path.join(SAVE_DIR, filename)
        pm_path = load_path.replace(".json", ".persistence.pickle")

        # Load files
        try:
            self.memgpt_agent.load_from_json_file_inplace(load_path)
        except Exception as e:
            print(f"Error loading profile from {load_path}: {e}")

        try:
            self.memgpt_agent.persistence_manager = InMemoryStateManager.load(pm_path)
        except Exception as e:
            print(f"Error loading persistence manager from {pm_path}: {e}")

        print(f"Loaded conversation from {load_path}")
        print(f"Loaded persistence manager from {pm_path}")


async def main():
    # Create chatbot
    chatbot = MemGPTChatbot()
    print("Debug: About to call load() from main()")  # Debug
    chatbot.load("fred_test.json")
    # Sample conversation
    messages = ["What did you do today?"]

    print("Debug: About to call chat()")  # Debug
    lastmessage = await chatbot.chat(messages)
    print(f"Debug: chat() called. Last message: {lastmessage}")  # Debug

    # Save state
    chatbot.save("fred_test.json")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


print("Script is being loaded.")
