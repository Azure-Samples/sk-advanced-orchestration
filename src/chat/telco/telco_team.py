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

kernel = create_kernel()

planned_team = PlannedTeam(
    id="planned-team",
    description="A special agent that can handle more complex asks by orchestrating multiple agents. Useful when user asks spans multiple domains.",
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
