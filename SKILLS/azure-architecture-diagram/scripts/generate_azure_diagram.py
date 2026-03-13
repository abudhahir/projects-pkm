#!/usr/bin/env python3
"""
Azure Architecture Diagram Generator
=====================================
Queries Azure CLI to discover all resources in a subscription and generates
a PNG architecture diagram using mingrammer/diagrams, grouped by resource group.

Usage:
    python generate_azure_diagram.py [OPTIONS]

Options:
    --subscription, -s  Azure subscription ID or name (default: current)
    --resource-group    Scope to a single resource group
    --input-file        Path to JSON file from 'az resource list' (skips live query)
    --output, -o        Output filename without extension (default: azure_architecture)
    --show              Open diagram in viewer after generation
    --dump-code         Print generated Python code and exit (do not render)
    --skip-prereq-check Skip prerequisite validation
    --help, -h          Show this help message

Examples:
    python generate_azure_diagram.py
    python generate_azure_diagram.py --subscription "My Subscription" --output prod_infra
    python generate_azure_diagram.py --subscription abc-123 --resource-group my-rg --show
    python generate_azure_diagram.py --input-file resources.json --output offline_diagram
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Azure resource type → (diagrams_module, class_name) mapping
# Resource types are lowercased for case-insensitive matching.
# Fall back to FALLBACK_NODE for unmapped types.
# ---------------------------------------------------------------------------
RESOURCE_TYPE_MAP: dict[str, tuple[str, str]] = {
    # ── Compute ─────────────────────────────────────────────────────────────
    "microsoft.compute/virtualmachines":                    ("diagrams.azure.compute", "VM"),
    "microsoft.compute/virtualmachinescalesets":            ("diagrams.azure.compute", "VMScaleSetLinux"),
    "microsoft.compute/disks":                              ("diagrams.azure.compute", "Disks"),
    "microsoft.compute/availabilitysets":                   ("diagrams.azure.compute", "AvailabilitySets"),
    "microsoft.compute/snapshots":                          ("diagrams.azure.compute", "Disks"),
    "microsoft.compute/images":                             ("diagrams.azure.compute", "VMImages"),
    "microsoft.compute/galleries":                          ("diagrams.azure.compute", "SharedImageGalleries"),
    "microsoft.containerservice/managedclusters":           ("diagrams.azure.compute", "KubernetesServices"),
    "microsoft.containerinstance/containergroups":          ("diagrams.azure.compute", "ContainerInstances"),
    "microsoft.containerregistry/registries":               ("diagrams.azure.compute", "ContainerRegistries"),
    "microsoft.app/containerapps":                          ("diagrams.azure.compute", "ContainerInstances"),
    "microsoft.app/managedenvironments":                    ("diagrams.azure.compute", "ContainerInstances"),
    # ── App Service / Web ───────────────────────────────────────────────────
    "microsoft.web/sites":                                  ("diagrams.azure.compute", "AppServices"),
    "microsoft.web/serverfarms":                            ("diagrams.azure.compute", "AppServicePlans"),
    "microsoft.web/staticwebsites":                         ("diagrams.azure.compute", "AppServices"),
    "microsoft.web/hostingenvironments":                    ("diagrams.azure.compute", "AppServiceEnvironments"),
    # ── Functions ───────────────────────────────────────────────────────────
    "microsoft.web/sites/functions":                        ("diagrams.azure.compute", "FunctionApps"),
    # ── Spring Cloud ────────────────────────────────────────────────────────
    "microsoft.appplatform/spring":                         ("diagrams.azure.compute", "SpringCloud"),
    # ── Databases ───────────────────────────────────────────────────────────
    "microsoft.sql/servers":                                ("diagrams.azure.database", "SQLServer"),
    "microsoft.sql/servers/databases":                      ("diagrams.azure.database", "SQLDatabases"),
    "microsoft.sql/servers/elasticpools":                   ("diagrams.azure.database", "SQLElasticPools"),
    "microsoft.sql/managedinstances":                       ("diagrams.azure.database", "SQLManagedInstances"),
    "microsoft.documentdb/databaseaccounts":                ("diagrams.azure.database", "CosmosDb"),
    "microsoft.dbforpostgresql/servers":                    ("diagrams.azure.database", "AzureDatabaseForPostgresql"),
    "microsoft.dbforpostgresql/flexibleservers":            ("diagrams.azure.database", "AzureDatabaseForPostgresql"),
    "microsoft.dbformysql/servers":                         ("diagrams.azure.database", "AzureDatabaseForMysql"),
    "microsoft.dbformysql/flexibleservers":                 ("diagrams.azure.database", "AzureDatabaseForMysql"),
    "microsoft.dbformariadb/servers":                       ("diagrams.azure.database", "AzureDatabaseForMysql"),
    "microsoft.cache/redis":                                ("diagrams.azure.database", "Cache"),
    "microsoft.synapse/workspaces":                         ("diagrams.azure.database", "SynapseAnalytics"),
    "microsoft.timeseriesinsights/environments":            ("diagrams.azure.database", "Timestream"),
    # ── Storage ─────────────────────────────────────────────────────────────
    "microsoft.storage/storageaccounts":                    ("diagrams.azure.storage", "StorageAccounts"),
    "microsoft.datalakestore/accounts":                     ("diagrams.azure.storage", "DataLakeStorage"),
    "microsoft.storage/storageaccounts/blobservices":       ("diagrams.azure.storage", "BlobStorage"),
    "microsoft.storage/storageaccounts/fileservices":       ("diagrams.azure.storage", "FileStorage"),
    "microsoft.storage/storageaccounts/tableservices":      ("diagrams.azure.storage", "TableStorage"),
    "microsoft.storage/storageaccounts/queueservices":      ("diagrams.azure.storage", "QueuesStorage"),
    "microsoft.storagesync/storagesyncservices":            ("diagrams.azure.storage", "StorageSyncServices"),
    "microsoft.databoxedge/databoxedgedevices":             ("diagrams.azure.storage", "DataBoxEdgeDataBoxGateway"),
    # ── Networking ──────────────────────────────────────────────────────────
    "microsoft.network/virtualnetworks":                    ("diagrams.azure.network", "VirtualNetworks"),
    "microsoft.network/loadbalancers":                      ("diagrams.azure.network", "LoadBalancers"),
    "microsoft.network/applicationgateways":                ("diagrams.azure.network", "ApplicationGateway"),
    "microsoft.network/publicipaddresses":                  ("diagrams.azure.network", "PublicIPAddresses"),
    "microsoft.network/networksecuritygroups":              ("diagrams.azure.network", "NetworkSecurityGroups"),
    "microsoft.network/dnszones":                           ("diagrams.azure.network", "DNSZones"),
    "microsoft.network/privatednszones":                    ("diagrams.azure.network", "DNSPrivateZones"),
    "microsoft.network/frontdoors":                         ("diagrams.azure.network", "FrontDoors"),
    "microsoft.network/trafficmanagerprofiles":             ("diagrams.azure.network", "TrafficManagerProfiles"),
    "microsoft.network/expressroutecircuits":               ("diagrams.azure.network", "ExpressrouteCircuits"),
    "microsoft.network/virtualnetworkgateways":             ("diagrams.azure.network", "VirtualNetworkGateways"),
    "microsoft.network/localnetworkgateways":               ("diagrams.azure.network", "LocalNetworkGateways"),
    "microsoft.network/connections":                        ("diagrams.azure.network", "Connections"),
    "microsoft.network/azurefirewalls":                     ("diagrams.azure.network", "Firewall"),
    "microsoft.network/firewallpolicies":                   ("diagrams.azure.network", "Firewall"),
    "microsoft.network/cdnprofiles":                        ("diagrams.azure.network", "CDNProfiles"),
    "microsoft.network/bastionhosts":                       ("diagrams.azure.security", "Bastion"),
    "microsoft.network/natgateways":                        ("diagrams.azure.network", "NATGateway"),
    "microsoft.network/routetables":                        ("diagrams.azure.network", "RouteTables"),
    "microsoft.network/privateendpoints":                   ("diagrams.azure.network", "PrivateEndpoint"),
    "microsoft.network/networkinterfaces":                  ("diagrams.azure.network", "NetworkInterfaces"),
    "microsoft.network/networkwatchers":                    ("diagrams.azure.network", "NetworkWatcher"),
    "microsoft.network/ddosprotectionplans":                ("diagrams.azure.network", "DDOSProtectionPlans"),
    "microsoft.network/ipgroups":                           ("diagrams.azure.network", "IPGroups"),
    "microsoft.cdn/profiles":                               ("diagrams.azure.network", "CDNProfiles"),
    # ── Security / Identity ─────────────────────────────────────────────────
    "microsoft.keyvault/vaults":                            ("diagrams.azure.security", "KeyVaults"),
    "microsoft.keyvault/managedhsms":                       ("diagrams.azure.security", "KeyVaults"),
    "microsoft.security/autoprovisioningsettings":          ("diagrams.azure.security", "SecurityCenter"),
    "microsoft.sentinel/workspaces":                        ("diagrams.azure.security", "Sentinel"),
    "microsoft.managedidentity/userassignedidentities":     ("diagrams.azure.security", "MicrosoftAntimalware"),
    # ── Integration & Messaging ─────────────────────────────────────────────
    "microsoft.servicebus/namespaces":                      ("diagrams.azure.integration", "ServiceBus"),
    "microsoft.eventhub/namespaces":                        ("diagrams.azure.integration", "EventHubs"),
    "microsoft.eventhub/clusters":                          ("diagrams.azure.integration", "EventHubClusters"),
    "microsoft.eventgrid/topics":                           ("diagrams.azure.integration", "EventGridTopics"),
    "microsoft.eventgrid/domains":                          ("diagrams.azure.integration", "EventGridDomains"),
    "microsoft.eventgrid/systemtopics":                     ("diagrams.azure.integration", "SystemTopic"),
    "microsoft.logic/workflows":                            ("diagrams.azure.integration", "LogicApps"),
    "microsoft.logic/integrationaccounts":                  ("diagrams.azure.integration", "IntegrationAccounts"),
    "microsoft.apimanagement/service":                      ("diagrams.azure.integration", "APIManagement"),
    "microsoft.appconfiguration/configurationstores":       ("diagrams.azure.integration", "AppConfiguration"),
    "microsoft.relay/namespaces":                           ("diagrams.azure.integration", "Relays"),
    # ── AI & Machine Learning ───────────────────────────────────────────────
    "microsoft.cognitiveservices/accounts":                 ("diagrams.azure.ml", "CognitiveServices"),
    "microsoft.machinelearningservices/workspaces":         ("diagrams.azure.ml", "MachineLearningServiceWorkspaces"),
    "microsoft.botservice/botservices":                     ("diagrams.azure.ml", "BotServices"),
    "microsoft.search/searchservices":                      ("diagrams.azure.ml", "CognitiveServices"),
    # ── Monitoring / Observability ──────────────────────────────────────────
    "microsoft.operationalinsights/workspaces":             ("diagrams.azure.devops", "Devops"),
    "microsoft.insights/components":                        ("diagrams.azure.devops", "ApplicationInsights"),
    "microsoft.insights/workbooks":                         ("diagrams.azure.devops", "Devops"),
    "microsoft.dashboard/grafana":                          ("diagrams.azure.devops", "Devops"),
    # ── DevOps / Developer Tools ────────────────────────────────────────────
    "microsoft.devtestlab/labs":                            ("diagrams.azure.devops", "Devops"),
    # ── Data Analytics ──────────────────────────────────────────────────────
    "microsoft.databricks/workspaces":                      ("diagrams.azure.analytics", "Databricks"),
    "microsoft.hdinsight/clusters":                         ("diagrams.azure.analytics", "HDInsightClusters"),
    "microsoft.datafactory/factories":                      ("diagrams.azure.analytics", "DataFactories"),
    "microsoft.analysisservices/servers":                   ("diagrams.azure.analytics", "AnalysisServices"),
    "microsoft.dataexplorer/clusters":                      ("diagrams.azure.analytics", "DataExplorerClusters"),
    "microsoft.purview/accounts":                           ("diagrams.azure.analytics", "DataCatalog"),
    "microsoft.streamanalytics/streamingjobs":              ("diagrams.azure.analytics", "StreamAnalyticsJobs"),
    # ── IoT ─────────────────────────────────────────────────────────────────
    "microsoft.devices/iothubs":                            ("diagrams.azure.iot", "IotHub"),
    "microsoft.devices/provisioningservices":               ("diagrams.azure.iot", "DeviceProvisioningServices"),
    "microsoft.digitaltwin/digitaltwinsinstances":          ("diagrams.azure.iot", "DigitalTwins"),
    "microsoft.timeseriesinsights/environments":            ("diagrams.azure.iot", "TimeSeriesInsightsEnvironments"),
    # ── Migration / Hybrid ──────────────────────────────────────────────────
    "microsoft.recoveryservices/vaults":                    ("diagrams.azure.migrate", "RecoveryServicesVaults"),
    "microsoft.migrate/migrateprojects":                    ("diagrams.azure.migrate", "DatabaseMigrationServices"),
}

# Used when a resource type has no specific mapping
FALLBACK_NODE = ("diagrams.azure.general", "Resourcegroups")

# Colour palette injected into graph_attr for cleaner rendering
GRAPH_ATTR = {
    "fontsize": "12",
    "bgcolor": "white",
    "pad": "0.75",
    "splines": "ortho",
    "nodesep": "0.60",
    "ranksep": "0.75",
}


# ---------------------------------------------------------------------------
# Azure CLI helpers
# ---------------------------------------------------------------------------

def _run_az(*args: str) -> list | dict:
    """Run an az CLI command, return parsed JSON. Raises RuntimeError on failure."""
    cmd = ["az", *args, "--output", "json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    text = result.stdout.strip()
    if not text:
        return []
    return json.loads(text)


def check_prerequisites() -> None:
    """Verify az CLI, diagrams library, and Graphviz are present."""
    errors: list[str] = []

    # Azure CLI
    r = subprocess.run(["az", "--version"], capture_output=True)
    if r.returncode != 0:
        errors.append(
            "  • Azure CLI (az) not found — https://docs.microsoft.com/cli/azure/install-azure-cli"
        )

    # diagrams
    r = subprocess.run(
        [sys.executable, "-c", "import diagrams"],
        capture_output=True,
    )
    if r.returncode != 0:
        errors.append("  • Python 'diagrams' package not installed — run: pip install diagrams")

    # Graphviz
    r = subprocess.run(["dot", "-V"], capture_output=True)
    if r.returncode != 0:
        errors.append(
            "  • Graphviz 'dot' not on PATH — https://graphviz.org/download/"
        )

    if errors:
        print("Missing prerequisites:\n" + "\n".join(errors))
        sys.exit(1)

    print("✓ All prerequisites satisfied")


def get_subscription_info(subscription_id: str | None) -> tuple[str, str]:
    """Return (subscription_id, subscription_name) for the specified or current subscription."""
    args = ["account", "show"]
    if subscription_id:
        args += ["--subscription", subscription_id]
    try:
        info = _run_az(*args)
    except RuntimeError as exc:
        raise RuntimeError(
            f"Cannot read subscription. Are you logged in? Run: az login\n{exc}"
        ) from exc
    return info["id"], info["name"]


def list_resources(subscription_id: str, resource_group: str | None = None) -> list[dict]:
    """Return all resources in the subscription (optionally filtered by resource group)."""
    args = ["resource", "list", "--subscription", subscription_id]
    if resource_group:
        args += ["--resource-group", resource_group]
    return _run_az(*args)  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def _sanitize_varname(name: str) -> str:
    """Convert an Azure resource name to a valid Python variable name."""
    var = re.sub(r"[^a-zA-Z0-9]", "_", name).lower().lstrip("_")
    if var and var[0].isdigit():
        var = "r_" + var
    return var or "resource"


def _collect_imports(resources: list[dict]) -> dict[str, set[str]]:
    """Build {module: {ClassName, ...}} for all resources."""
    imports: dict[str, set[str]] = defaultdict(set)
    for r in resources:
        rtype = r.get("type", "").lower()
        mod, cls = RESOURCE_TYPE_MAP.get(rtype, FALLBACK_NODE)
        imports[mod].add(cls)
    return imports


def _label(name: str, max_len: int = 32) -> str:
    """Truncate long names for diagram readability."""
    return name if len(name) <= max_len else name[: max_len - 3] + "..."


def generate_diagram_code(
    sub_name: str,
    resources: list[dict],
    output_filename: str,
    show: bool = False,
) -> str:
    """Return the complete Python source for a mingrammer/diagrams diagram."""
    by_rg: dict[str, list[dict]] = defaultdict(list)
    for r in resources:
        rg = r.get("resourceGroup") or "Ungrouped"
        by_rg[rg].append(r)

    imports = _collect_imports(resources)

    lines: list[str] = [
        "# ── Auto-generated Azure architecture diagram ──────────────────────────────",
        "# Generated by the azure-architecture-diagram skill",
        "# DO NOT EDIT — re-run generate_azure_diagram.py to refresh",
        "from diagrams import Cluster, Diagram",
        "",
    ]

    for mod in sorted(imports):
        classes = ", ".join(sorted(imports[mod]))
        lines.append(f"from {mod} import {classes}")

    # Build graph_attr literal
    graph_attr_lines = [f'    "{k}": "{v}",' for k, v in GRAPH_ATTR.items()]
    lines += [
        "",
        "graph_attr = {",
        *graph_attr_lines,
        "}",
        "",
        "with Diagram(",
        f'    "{_label(sub_name, 60)}\\nAzure Architecture",',
        f'    filename="{output_filename}",',
        f"    show={show},",
        '    direction="TB",',
        "    graph_attr=graph_attr,",
        "):",
    ]

    for rg_name, rg_resources in sorted(by_rg.items()):
        lines.append(f'    with Cluster("Resource Group: {rg_name}"):')
        seen_vars: dict[str, int] = {}
        for r in rg_resources:
            rtype = r.get("type", "").lower()
            rname = r.get("name", "unnamed")
            _, cls = RESOURCE_TYPE_MAP.get(rtype, FALLBACK_NODE)
            base_var = _sanitize_varname(rname)
            if base_var in seen_vars:
                seen_vars[base_var] += 1
                var = f"{base_var}_{seen_vars[base_var]}"
            else:
                seen_vars[base_var] = 1
                var = base_var
            lines.append(f'        {var} = {cls}("{_label(rname)}")')
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an Azure architecture diagram using mingrammer/diagrams",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--subscription", "-s",
        help="Azure subscription ID or display name (default: current account)",
    )
    parser.add_argument(
        "--resource-group",
        help="Limit diagram to a single resource group",
    )
    parser.add_argument(
        "--input-file",
        help="Path to pre-fetched JSON from 'az resource list -o json' (skips live query)",
    )
    parser.add_argument(
        "--output", "-o",
        default="azure_architecture",
        help="Output filename without extension (default: azure_architecture)",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Open the generated PNG in the default viewer",
    )
    parser.add_argument(
        "--dump-code",
        action="store_true",
        help="Print generated Python code and exit without rendering",
    )
    parser.add_argument(
        "--skip-prereq-check",
        action="store_true",
        help="Skip prerequisite validation checks",
    )
    args = parser.parse_args()

    if not args.skip_prereq_check:
        check_prerequisites()

    # ── Resolve subscription ─────────────────────────────────────────────────
    try:
        sub_id, sub_name = get_subscription_info(args.subscription)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    print(f"Subscription : {sub_name}")
    print(f"ID           : {sub_id}")
    if args.resource_group:
        print(f"Resource Group Filter: {args.resource_group}")

    # ── Fetch resources ──────────────────────────────────────────────────────
    if args.input_file:
        print(f"Loading resources from: {args.input_file}")
        with open(args.input_file, encoding="utf-8") as f:
            resources: list[dict] = json.load(f)
    else:
        print("Querying Azure resources (this may take a moment)...")
        try:
            resources = list_resources(sub_id, args.resource_group)
        except RuntimeError as exc:
            print(f"ERROR: Failed to list resources.\n{exc}")
            sys.exit(1)

    if not resources:
        print("WARNING: No resources found. Verify the subscription/resource group and your Reader permissions.")
        sys.exit(0)

    # Summarise what was found
    rtype_counts: dict[str, int] = defaultdict(int)
    for r in resources:
        rtype_counts[r.get("type", "Unknown")] += 1
    print(f"\nFound {len(resources)} resources across {len(rtype_counts)} resource types:")
    for rtype, count in sorted(rtype_counts.items(), key=lambda x: -x[1])[:20]:
        mapped = "✓" if rtype.lower() in RESOURCE_TYPE_MAP else "~"
        print(f"  {mapped}  {count:4d}  {rtype}")
    if len(rtype_counts) > 20:
        print(f"  ... and {len(rtype_counts) - 20} more types")
    print()

    # ── Generate diagram code ────────────────────────────────────────────────
    code = generate_diagram_code(sub_name, resources, args.output, args.show)

    if args.dump_code:
        print(code)
        return

    # ── Write generated code to a temp file and execute ─────────────────────
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        prefix="azure_diagram_",
        encoding="utf-8",
    ) as tmp:
        tmp.write(code)
        tmp_path = tmp.name

    print(f"Rendering diagram...")
    render_result = subprocess.run(
        [sys.executable, tmp_path],
        capture_output=True,
        text=True,
    )
    os.unlink(tmp_path)

    if render_result.returncode != 0:
        print("ERROR: Diagram rendering failed.\n")
        print("─── stderr ───────────────────────────────────────────────────────────")
        print(render_result.stderr)
        print("─── Generated code (for debugging) ───────────────────────────────────")
        print(code)
        sys.exit(1)

    # ── Report output ────────────────────────────────────────────────────────
    output_path = Path(args.output).with_suffix(".png")
    if output_path.exists():
        size_kb = output_path.stat().st_size // 1024
        print(f"✓ Diagram saved: {output_path.resolve()}  ({size_kb} KB)")
    else:
        # diagrams may add its own path logic
        print(f"✓ Diagram rendered. Look for: {args.output}.png")

    print("\nTip: Run with --dump-code to inspect the generated Python before rendering.")
    print("Tip: Edit the generated code to add Edge(...) connections for richer diagrams.")


if __name__ == "__main__":
    main()
