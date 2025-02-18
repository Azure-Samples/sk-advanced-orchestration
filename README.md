# Semantic Kernel Agentic Call Center

This project is a call center application that uses a semantic kernel to understand the intent of the caller and route the call to the appropriate agent, levering a smarter `SelectionStrategy` and featuring _nested_ `Teams` and `Agents` for more complex routing scenarios. It also includes a special kind of
`Agent` that constructs a `PlannedTeam` where more complex asks are turned into a multi-step process.

The overall architecture includes Dapr to enable _Virtual Actor pattern_, in order to host the agentic team and natively handle `ChatHistory` persistence via Dapr's state store.

## Features

## Getting Started

### Prerequisites

- **Python 3.12+** – Ensure you have a compatible Python version.
- **Azure Developer CLI** – To deploy and manage Azure resources.
- **Dapr CLI** – To run the application locally.

### Installation

## License

This project is open source. See the [LICENSE](LICENSE) file for details.

```

```
