import logging

from collections.abc import AsyncIterable
from typing import Any, ClassVar

from semantic_kernel.agents import Agent
from semantic_kernel.agents.strategies.selection.selection_strategy import (
    SelectionStrategy,
)
from semantic_kernel.agents.strategies.termination.termination_strategy import (
    TerminationStrategy,
)
from semantic_kernel.utils.telemetry.agent_diagnostics.decorators import (
    trace_agent_invocation,
)
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.streaming_chat_message_content import (
    StreamingChatMessageContent,
)
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.exceptions.agent_exceptions import AgentChatException
from semantic_kernel.agents.channels.agent_channel import AgentChannel
from semantic_kernel.agents.channels.chat_history_channel import ChatHistoryChannel

logger: logging.Logger = logging.getLogger(__name__)


class Team(Agent):
    id: str
    description: str
    agents: list[Agent]
    selection_strategy: SelectionStrategy
    termination_strategy: TerminationStrategy
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
        channel = await self.create_channel()
        channel.receive(history.messages)

        for _ in range(self.termination_strategy.maximum_iterations):
            try:
                selected_agent = await self.selection_strategy.next(
                    self.agents, history.messages
                )
            except Exception as ex:
                logger.error(f"Failed to select agent: {ex}")
                raise AgentChatException("Failed to select agent") from ex

            async for is_visible, message in channel.invoke(selected_agent):
                history.add_message(message)
                if message.role == AuthorRole.ASSISTANT:
                    task = self.termination_strategy.should_terminate(
                        selected_agent, history.messages
                    )
                    self.is_complete = await task

                if is_visible:
                    yield message

            if self.is_complete:
                break

    @trace_agent_invocation
    async def invoke_stream(
        self,
        history: ChatHistory,
        arguments: KernelArguments | None = None,
        kernel: "Kernel | None" = None,
        **kwargs: Any,
    ) -> AsyncIterable[StreamingChatMessageContent]:
        raise NotImplementedError("Stream invocation is not supported for Team agent")
