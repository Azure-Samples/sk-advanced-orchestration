from dotenv import load_dotenv

load_dotenv(override=True)

import chainlit as cl

from semantic_kernel.contents import ChatHistory

from speaker_election_strategy import SpeakerElectionStrategy
from termination_strategy import UserInputRequiredTerminationStrategy
from basic_kernel import create_kernel

from telco.sales import sales_agent
from telco.technical import technical_agent
from telco.user import user_agent
from telco.billing import billing_agent
from team import Team

from planning_strategy import DefaultPlanningStrategy
from feedback_strategy import DefaultFeedbackStrategy
from planned_team import PlannedTeam

import logging

logger = logging.getLogger(__name__)
logging.getLogger("semantic_kernel").setLevel(logging.WARN)

kernel = create_kernel()

planned_team = PlannedTeam(
    id="planned-team",
    description="A stronger agent with more capabilities, can handle more complex queries that other agents can't single-handedly but requires more time to plan",
    agents=[sales_agent, technical_agent, billing_agent],
    planning_strategy=DefaultPlanningStrategy(
        kernel=kernel, include_tools_descriptions=True
    ),
    feedback_strategy=DefaultFeedbackStrategy(kernel=kernel),
)
team = Team(
    id="customer-support",
    description="Customer support team",
    agents=[user_agent, sales_agent, technical_agent, billing_agent, planned_team],
    selection_strategy=SpeakerElectionStrategy(kernel=kernel),
    termination_strategy=UserInputRequiredTerminationStrategy(stop_agents=[user_agent]),
)


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
    # logger.info("\n".join([f"[{msg.name}]: {msg.content}" for msg in history.messages]))
