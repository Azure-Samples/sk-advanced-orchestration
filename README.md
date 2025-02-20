# Semantic Kernel Advanced Customer Support

This repo contains a sample customer support application that uses [Semantic Kernel](https://github.com/microsoft/semantic-kernel) Agents levering an improved [`SelectionStrategy`](src/agents/sk_ext/speaker_election_strategy.py) that accounts for agents descriptions and available tools to provide a more accurate selection (including the reason for it for traceability).

It also features _nested orchestration_ via [`Teams`](src/agents/sk_ext/team.py) and `Agents` for more complex, hierarchical routing scenarios.

It also includes a special kind of
`Agent` that constructs a [`PlannedTeam`](src/agents/sk_ext/planned_team.py) where more complex asks are turned into a multi-step process.

## Example

![Example chat demonstrating agents producing a composite answer](image.png)

## Architecture

The overall architecture involves [Dapr](https://dapr.io) to enable the [_Virtual Actor pattern_](https://docs.dapr.io/developing-applications/building-blocks/actors/actors-overview/), in order to host the agentic team and natively handle `ChatHistory` persistence via Dapr's [state store](https://docs.dapr.io/developing-applications/building-blocks/state-management/).

```mermaid
flowchart TD
  %% User and client
  U[User]
  CB[Browser / Client]
  U --> CB

  %% Container Apps (Dapr enabled)
  subgraph "Azure Container Apps"
    Chat["`Chat App<br/>(Dapr enabled)<br/>[src/chat]`"]
    Agents["`Agents App<br/>(Dapr enabled)<br/>[src/agents]`"]
  end

  CB --> Chat

  %% Dapr sidecars within container apps
  Chat -- "Dapr Sidecar" --> DS1["`Dapr: state store<br/>(in-memory / Cosmos DB)`"]
  Agents -- "Dapr Sidecar" --> DS2[Dapr Components]

  %% Communication Flow
  Chat --- Agents
  Agents --- Chat

  %% Azure Services and Infrastructure
  subgraph "Azure Resources"
    ACR["`Azure Container Registry<br/>[infra/acr.bicep]`"]
    AI["`Application Insights<br/>[infra/appin.bicep]`"]
    LA["`Log Analytics<br/>[infra/appin.bicep]`"]
    OAI["`Azure OpenAI<br/>[infra/openAI.bicep]`"]
    Cosmos["`Cosmos DB<br/>[infra/cosmos.bicep]`"]
    UAMI["`User Assigned Identity<br/>[infra/uami.bicep]`"]
  end

  %% Deployment orchestration via Azure Developer CLI
  ADCLI["`Azure Developer CLI<br/>(azd)`"]
  ADCLI --> ACR
  ADCLI --> AI
  ADCLI --> LA
  ADCLI --> OAI
  ADCLI --> Cosmos
  ADCLI --> UAMI

  %% Container App image source
  ACR --> Chat
  ACR --> Agents

  %% Monitoring and Telemetry
  Chat --> AI
  Agents --> AI
  AI --> LA

  %% Data persistence via Dapr state store
  DS1 --> Cosmos

  %% Semantic Kernel
  SK["`Semantic Kernel<br/>(LLM Processing)`"]
  Agents --> SK
  SK --- Agents
```

## Getting Started

### Prerequisites

- **Python 3.12+**
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

# When prompted, select
# - Azure subscription to deploy to
# - Azure region to deploy to
# - Azure OpenAI resource and group to use
```

### Running Locally

1. `cp .env.example .env`
2. Update `.env` with your Azure OpenAI resource endpoint
3. Ensure Docker is running.
4. Init Dapr (once only): `dapr init`.

To run:

`dapr run -f dapr.yaml`

## Contributing

This project welcomes contributions and suggestions. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License. See [LICENSE.md](LICENSE.md) for details.
