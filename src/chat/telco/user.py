from semantic_kernel.agents import ChatCompletionAgent
from basic_kernel import create_kernel

user_agent = ChatCompletionAgent(
    id="user_agent",
    kernel=create_kernel(),
    description="A human user that interacts with the system. Can provide input to the chat",
    instructions="Always responde PAUSE",
)
