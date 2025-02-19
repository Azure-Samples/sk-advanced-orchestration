# Semantic Kernel Advanced Customer Support

This project is a customer support application that uses a [Semantic Kernel](https://github.com/microsoft/semantic-kernel) to understand the intent of the caller and route the call to the appropriate agent, levering a smarter `SelectionStrategy` and featuring _nested_ `Teams` and `Agents` for more complex, hierarchical routing scenarios. It also includes a special kind of
`Agent` that constructs a `PlannedTeam` where more complex asks are turned into a multi-step process.

The overall architecture includes Dapr to enable _Virtual Actor pattern_, in order to host the agentic team and natively handle `ChatHistory` persistence via Dapr's state store.

## Getting Started

### Prerequisites

- **Python 3.12+** – Ensure you have a compatible Python version.
- [**Azure Developer CLI**](https://learn.microsoft.com/en-us/azure/developer/azure-developer-cli/install-azd?tabs=winget-windows%2Cbrew-mac%2Cscript-linux&pivots=os-windows) – To deploy and manage Azure resources.
- **Docker** and [**Dapr CLI**](https://docs.dapr.io/getting-started/install-dapr-cli/) – To run the application locally.

### Clone the repo

```bash
git clone https://github.com/Azure-Samples/mas-sk-quickstart
cd mas-sk-quickstart
```

### Azure Deployment

```bash
# Login to Azure if required
azd auth login --tenant-id <TENANT>.onmicrosoft.com

azd up
```

### Running Locally

1. Ensure Docker is running.
2. Init Dapr (once only): `dapr init`.
3. Run the application: `dapr run -f dapr.yaml`

## License

This project is open source. See the [LICENSE](LICENSE) file for details.
