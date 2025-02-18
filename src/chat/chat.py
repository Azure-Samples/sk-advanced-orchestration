from dotenv import load_dotenv

load_dotenv(override=True)

import chainlit as cl

from semantic_kernel.contents import ChatHistory

from telco.telco_team import team
import logging

# import debugpy
# # Start the debug server on port 5678
# debugpy.listen(("localhost", 5678))

logger = logging.getLogger(__name__)
logging.getLogger("semantic_kernel").setLevel(logging.WARN)
logging.getLogger("chat").setLevel(logging.DEBUG)


def create_history():
    cl.user_session.set("history", ChatHistory())


@cl.on_chat_start
async def on_start():
    """
    This function is called when the chat is started.
    """
    create_history()


@cl.on_message
async def on_message(message: cl.Message):
    """
    This function is called when a message is received from the user.
    """
    history: ChatHistory = cl.user_session.get("history")

    history.add_user_message(message.content)

    async for result in team.invoke(history=history):
        logger.info(f"Result: {result}")
        if "PAUSE" not in result.content:
            await cl.Message(content=result.content, author=result.name).send()

    cl.user_session.set("history", history)
