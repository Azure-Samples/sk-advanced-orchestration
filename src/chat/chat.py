from dotenv import load_dotenv

load_dotenv(override=True)

import chainlit as cl

from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.contents import ChatHistory

from speaker_election_strategy import SpeakerElectionStrategy
from termination_strategy import UserInputRequiredTerminationStrategy
from basic_kernel import create_kernel

from telco.sales import sales_agent
from telco.technical import technical_agent
from telco.user import user_agent
from team import Team

import logging

logger = logging.getLogger(__name__)


def create_team():
    team = AgentGroupChat(
        agents=[user_agent, sales_agent, technical_agent],
        termination_strategy=UserInputRequiredTerminationStrategy(
            stop_agents=[user_agent]
        ),
        selection_strategy=SpeakerElectionStrategy(kernel=create_kernel()),
    )
    cl.user_session.set("team", team)


team = Team(
    id="customer-support",
    description="Customer support team",
    agents=[user_agent, sales_agent, technical_agent],
    selection_strategy=SpeakerElectionStrategy(kernel=create_kernel()),
    termination_strategy=UserInputRequiredTerminationStrategy(stop_agents=[user_agent]),
)


def create_history():
    cl.user_session.set("history", ChatHistory())


@cl.on_chat_start
async def on_start():
    """
    This function is called when the chat is started.
    """
    # create_team()
    create_history()


@cl.on_message
async def on_message(message: cl.Message):
    """
    This function is called when a message is received from the user.
    """
    # team: AgentGroupChat = cl.user_session.get("team")
    # # https://learn.microsoft.com/en-us/semantic-kernel/frameworks/agent/agent-chat?pivots=programming-language-python#resetting-chat-completion-state
    # team.is_complete = False

    # await team.add_chat_message(
    #     ChatMessageContent(
    #         role=AuthorRole.USER,
    #         content=message.content,
    #     )
    # )

    # async for result in team.invoke():
    #     if "PAUSE" not in result.content:
    #         await cl.Message(content=result.content, author=result.name).send()
    history: ChatHistory = cl.user_session.get("history")

    history.add_user_message(message.content)

    async for result in team.invoke(history=history):
        logger.info(f"Result: {result}")
        if "PAUSE" not in result.content:
            await cl.Message(content=result.content, author=result.name).send()

    cl.user_session.set("history", history)
    logger.info("\n".join([f"[{msg.name}]: {msg.content}" for msg in history.messages]))
