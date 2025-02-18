from dotenv import load_dotenv

load_dotenv(override=True)

import chainlit as cl

from dapr.actor import ActorInterface, actormethod, ActorProxy, ActorId
from semantic_kernel.contents.chat_message_content import ChatMessageContent


class SKAgentActorInterface(ActorInterface):
    @actormethod(name="invoke")
    async def invoke(self, input_message: str) -> list[dict]: ...

    @actormethod(name="get_history")
    async def get_history(self) -> dict: ...


import logging

# import debugpy
# # Start the debug server on port 5678
# debugpy.listen(("localhost", 5678))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Ensure logging level is set as required


@cl.on_message
async def on_message(message: cl.Message):
    """
    This function is called when a message is received from the user.
    """
    session_id = cl.user_session.get("id")
    proxy: SKAgentActorInterface = ActorProxy.create(
        actor_type="SKAgentActor",
        actor_id=ActorId(session_id),
        actor_interface=SKAgentActorInterface,
    )

    results = await proxy.invoke(message.content)
    for result in results:
        response = ChatMessageContent.model_validate(result)
        logger.debug(f"Received result from agent: {result}")
        if "PAUSE" not in response.content:
            await cl.Message(content=response.content, author=response.name).send()
