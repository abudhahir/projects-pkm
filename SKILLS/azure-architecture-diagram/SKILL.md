---
name: azure-architecture-diagram
description: This skill should be used when a user wants to generate a visual architecture diagram of an Azure subscription's infrastructure. It discovers all resources via Azure CLI (or Azure MCP if available), maps them to mingrammer/diagrams Python nodes, generates executable Python code, and renders a PNG architecture diagram grouped by resource group. Trigger phrases include "generate azure diagram", "visualize azure subscription", "draw my azure infrastructure", "create azure architecture diagram", "diagram my azure resources", "map my azure environment".
version: 1.0.0
---

# Azure Architecture Diagram

Dynamically discover and render a visual PNG architecture diagram of any Azure subscription using Azure CLI and [mingrammer/diagrams](https://diagrams.mingrammer.com/).

## Prerequisites

Before running, verify the following are available:

| Dependency | Check | Install |
|---|---|---|
| Azure CLI | `az --version` | https://docs.microsoft.com/cli/azure/install-azure-cli |
| Python diagrams | `python -c "import diagrams"` | `pip install diagrams` |
| Graphviz | `dot -V` | https://graphviz.org/download/ |
| Azure login | `az account show` | `az login` |

If any are missing, inform the user and show the install command before proceeding.

## Workflow

### Step 1 — Gather scope from the user

Ask (or infer from context) the following if not already provided:
- **Subscription**: ID, name, or "current" (default)
- **Filter**: Specific resource group(s), or all (default)
- **Output file**: Where to save the PNG (default: `azure_architecture.png` in current directory)

### Step 2 — Verify Azure authentication

Run in terminal:
```bash
az account show --output table
```
If this fails, prompt the user to run `az login` or `az login --tenant <tenant-id>`.

### Step 3 — Run the generator script

The skill bundles a complete generator at `scripts/generate_azure_diagram.py`. Execute it:

```bash
# Full subscription (current default)
python scripts/generate_azure_diagram.py

# Specific subscription
python scripts/generate_azure_diagram.py --subscription <subscription-id-or-name>

# Filter to one resource group
python scripts/generate_azure_diagram.py --subscription <id> --resource-group <rg-name>

# Custom output file
python scripts/generate_azure_diagram.py --output my_infra --show
```

**Always use the script path relative to the skill directory**, or provide the absolute path.

### Step 4 — Inspect, iterate, or customize

After generation, the script writes the intermediate Python code to stdout so the agent can:
- **Show the generated code** to the user on request
- **Patch the code** to add manual edges, override labels, or change clustering
- **Re-run** with `--show` to auto-open the PNG after rendering

### Step 5 — Enhance with topology (optional)

For richer diagrams with network connections, run supplementary queries then patch the generated code:

```bash
# Get VNet peerings and subnets
az network vnet list --subscription <id> -o json

# Get AKS node pools
az aks list --subscription <id> -o json

# Get App Service connections
az webapp list --subscription <id> -o json
az webapp config connection-string list --name <app> --resource-group <rg> -o json
```

Use the reference file `references/azure-node-mapping.md` to manually add `Edge(...)` connections between identified components in the generated code.

## Key Behaviors

- **Group by resource group**: All resources are clustered inside their resource group using `Cluster`.
- **Unknown resource types**: Resources with no mapping fall back to a generic `Resourcegroups` icon. These are still rendered — they just use the Azure general icon.
- **Large subscriptions**: Subscriptions with 500+ resources create crowded diagrams. Recommend filtering by resource group (`--resource-group`) or resource type category.
- **Azure MCP**: If Azure MCP tools are available in the session (e.g., `azure_resource_list`), they can be used instead of Azure CLI for resource discovery. Pass the resulting JSON to the script via `--input-file`.
- **Subscription Name**: Shown as the diagram title, taken from `az account show`.

## Troubleshooting

| Problem | Solution |
|---|---|
| `az` not found | Install Azure CLI and restart terminal |
| `AuthorizationFailed` | Ensure the user has `Reader` role on the subscription |
| `ModuleNotFoundError: diagrams` | Run `pip install diagrams` |
| `ExecutableNotFound: dot` | Install Graphviz and ensure it's on PATH |
| Empty diagram | Subscription may have no resources — verify with `az resource list --output table` |
| Diagram too crowded | Use `--resource-group <name>` to scope to a single RG |

## Example Output Structure

```
azure_architecture.png
  └── [Diagram: "My Subscription - Azure Architecture"]
       ├── Cluster: Resource Group: production-rg
       │    ├── VM: web-server-01
       │    ├── VM: web-server-02
       │    ├── LoadBalancers: prod-lb
       │    └── StorageAccounts: prodstg01
       ├── Cluster: Resource Group: data-rg
       │    ├── SQLServer: prod-sql
       │    ├── CosmosDb: prod-cosmos
       │    └── Cache: prod-redis
       └── Cluster: Resource Group: networking-rg
            ├── VirtualNetworks: prod-vnet
            ├── ApplicationGateway: prod-agw
            └── Firewall: prod-fw
```

See `references/azure-node-mapping.md` for the full list of supported Azure resource types and their diagram node classes.
