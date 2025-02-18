import logging

from collections.abc import AsyncIterable
from typing import Any, ClassVar

from semantic_kernel.agents import Agent
from semantic_kernel.kernel import Kernel
from semantic_kernel.utils.telemetry.agent_diagnostics.decorators import (
    trace_agent_invocation,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.contents.streaming_chat_message_content import (
    StreamingChatMessageContent,
)
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.agents.channels.agent_channel import AgentChannel
from semantic_kernel.agents.channels.chat_history_channel import ChatHistoryChannel

from sk_ext.feedback_strategy import FeedbackStrategy
from sk_ext.planning_strategy import PlanningStrategy

logger = logging.getLogger(__name__)


class PlannedTeam(Agent):
    id: str
    description: str
    agents: list[Agent]
    planning_strategy: PlanningStrategy
    feedback_strategy: FeedbackStrategy
    channel_type: ClassVar[type[AgentChannel]] = ChatHistoryChannel
    is_complete: bool = False

    @trace_agent_invocation
    async def invoke(
        self,
        history: ChatHistory,
        arguments: KernelArguments | None = None,
        kernel: "Kernel | None" = None,
        **kwargs: Any,
    ) -> AsyncIterable[ChatMessageContent]:
        # In case the agent is invoked multiple times
        self.is_complete = False
        feedback: str = ""

        # Channel required to communicate with agents
        channel = await self.create_channel()
        await channel.receive(history.messages)

        while not self.is_complete:
            plan = await self.planning_strategy.create_plan(
                self.agents, history.messages, feedback
            )

            for step in plan.plan:
                # Pick next agent to execute the step
                selected_agent = next(
                    agent for agent in self.agents if agent.id == step.agent_id
                )
                # And add the step instructions to the history
                history.add_message(
                    ChatMessageContent(
                        role=AuthorRole.ASSISTANT,
                        name=self.id,
                        content=step.instructions,
                    )
                )

                # Then invoke the agent
                async for is_visible, message in channel.invoke(selected_agent):
                    history.add_message(message)

                    if is_visible:
                        yield message

            ok, feedback = await self.feedback_strategy.provide_feedback(
                history.messages
            )
            self.is_complete = ok

    @trace_agent_invocation
    async def invoke_stream(
        self,
        history: ChatHistory,
        arguments: KernelArguments | None = None,
        kernel: "Kernel | None" = None,
        **kwargs: Any,
    ) -> AsyncIterable[StreamingChatMessageContent]:
        # In case the agent is invoked multiple times
        self.is_complete = False
        feedback: str = ""

        # Channel required to communicate with agents
        channel = await self.create_channel()
        await channel.receive(history.messages)

        while not self.is_complete:
            plan = await self.planning_strategy.create_plan(
                self.agents, history.messages, feedback
            )

            for step in plan.plan:
                selected_agent = next(
                    agent for agent in self.agents if agent.id == step.agent_id
                )
                history.add_message(
                    ChatMessageContent(
                        role=AuthorRole.ASSISTANT,
                        name=self.id,
                        content=step.instructions,
                    )
                )

                messages: list[ChatMessageContent] = []

                async for message in channel.invoke_stream(selected_agent, messages):
                    yield message

                for message in messages:
                    history.messages.append(message)

            ok, feedback = await self.feedback_strategy.provide_feedback(
                history.messages
            )
            self.is_complete = ok
