from typing import Annotated
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function
from basic_kernel import create_kernel


class TechnicalAgentPlugin:
    @kernel_function
    def get_service_status(
        service_sku: Annotated[str, "The SKU of the service to check status for"]
    ) -> Annotated[str, "Status of the specified service"]:

        return "Service degraded"

    @kernel_function
    def check_customer_telemetry(
        service_sku: Annotated[
            str,
            "The SKU of the service to check status for, values can be INET_MOBILE, INET_BUNDLE, INET_HOME",
        ],
        customerCode: Annotated[str, "The customer code to check telemetry for"],
    ) -> Annotated[str, "Telemetry summary for the specified customer"]:

        return "No issues detected"


technical_agent_kernel = create_kernel()

technical_agent_kernel.add_plugin(TechnicalAgentPlugin, plugin_name="TechnicalAgent")


technical_agent = ChatCompletionAgent(
    description="A technical support agent that can answer technical questions",
    id="technical",
    kernel=technical_agent_kernel,
    instructions="""You are a technical support agent that responds to customer inquiries.
    
    Your task are:
    - Assess the technical issue the customer is facing.
    - Verify if there any known issues with the service the customer is using.
    - Check remote telemetry data to identify potential issues with customer's device. Be sure to ask customer code first.
    - Provide the customer with possible solutions to the issue. See the list of common issues below.
    - When the service status is OK, reply the customer and suggest to restart the device.
    - When the service status is DEGRADED, apologize to the customer and kindly ask them to wait for the issue to be resolved.
    - Open an internal ticket if the issue cannot be resolved immediately.
    
    Make sure to act politely and professionally.    
    
    ### Common issues and solutions:

    - Home Internet:
        - Issue: No internet connection.
        - Solutions: 
            - Check the router's power supply and cables.
            - Restart the router.
            - Check the internet connection status LED on the router.
    - Mobile Internet:
        - Issue: Slow internet connection or no connection.
        - Solutions:
            - Check the signal strength on the device.
            - Restart the device.
            - Check the data usage on the device.
            - Suggest the customer to purchase additional data when the limit is reached.
    - All-in-One Bundle:
        USE a combination of the solutions for Home Internet and Mobile Internet.
    
    """,
)
