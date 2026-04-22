# Azure Resource Type → Diagrams Node Mapping

Reference table for all supported Azure resource types and their corresponding
[mingrammer/diagrams](https://diagrams.mingrammer.com/) node classes.

Use this when manually patching generated diagram code to add connections, swap icons,
or add resource types not yet covered by the automatic mapping.

---

## Compute

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.Compute/virtualMachines` | `diagrams.azure.compute` | `VM` |
| `Microsoft.Compute/virtualMachineScaleSets` | `diagrams.azure.compute` | `VMScaleSetLinux` |
| `Microsoft.Compute/disks` | `diagrams.azure.compute` | `Disks` |
| `Microsoft.Compute/availabilitySets` | `diagrams.azure.compute` | `AvailabilitySets` |
| `Microsoft.Compute/snapshots` | `diagrams.azure.compute` | `Disks` |
| `Microsoft.Compute/images` | `diagrams.azure.compute` | `VMImages` |
| `Microsoft.Compute/galleries` | `diagrams.azure.compute` | `SharedImageGalleries` |
| `Microsoft.ContainerService/managedClusters` | `diagrams.azure.compute` | `KubernetesServices` |
| `Microsoft.ContainerInstance/containerGroups` | `diagrams.azure.compute` | `ContainerInstances` |
| `Microsoft.ContainerRegistry/registries` | `diagrams.azure.compute` | `ContainerRegistries` |
| `Microsoft.App/containerApps` | `diagrams.azure.compute` | `ContainerInstances` |
| `Microsoft.App/managedEnvironments` | `diagrams.azure.compute` | `ContainerInstances` |
| `Microsoft.AppPlatform/Spring` | `diagrams.azure.compute` | `SpringCloud` |

**All available compute classes:**
```python
from diagrams.azure.compute import (
    AKS, AppServiceEnvironments, AppServicePlans, AppServices,
    AvailabilitySets, BatchAccounts, ContainerInstances, ContainerRegistries,
    Disks, FunctionApps, KubernetesServices, SharedImageGalleries,
    SpringCloud, VM, VMImages, VMLinux, VMScaleSetLinux, VMScaleSetWindows,
    VMWindows, Workspaces
)
```

---

## App Service / Web

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.Web/sites` | `diagrams.azure.compute` | `AppServices` |
| `Microsoft.Web/serverFarms` | `diagrams.azure.compute` | `AppServicePlans` |
| `Microsoft.Web/staticSites` | `diagrams.azure.compute` | `AppServices` |
| `Microsoft.Web/hostingEnvironments` | `diagrams.azure.compute` | `AppServiceEnvironments` |

---

## Databases

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.Sql/servers` | `diagrams.azure.database` | `SQLServer` |
| `Microsoft.Sql/servers/databases` | `diagrams.azure.database` | `SQLDatabases` |
| `Microsoft.Sql/servers/elasticPools` | `diagrams.azure.database` | `SQLElasticPools` |
| `Microsoft.Sql/managedInstances` | `diagrams.azure.database` | `SQLManagedInstances` |
| `Microsoft.DocumentDB/databaseAccounts` | `diagrams.azure.database` | `CosmosDb` |
| `Microsoft.DBforPostgreSQL/servers` | `diagrams.azure.database` | `AzureDatabaseForPostgresql` |
| `Microsoft.DBforPostgreSQL/flexibleServers` | `diagrams.azure.database` | `AzureDatabaseForPostgresql` |
| `Microsoft.DBforMySQL/servers` | `diagrams.azure.database` | `AzureDatabaseForMysql` |
| `Microsoft.DBforMySQL/flexibleServers` | `diagrams.azure.database` | `AzureDatabaseForMysql` |
| `Microsoft.Cache/Redis` | `diagrams.azure.database` | `Cache` |
| `Microsoft.Synapse/workspaces` | `diagrams.azure.database` | `SynapseAnalytics` |

**All available database classes:**
```python
from diagrams.azure.database import (
    AzureCosmosDb, AzureDatabaseForMysql, AzureDatabaseForPostgresql,
    Cache, CosmosDb, DataFactory, DatabaseForMysql, DatabaseForPostgresql,
    ManagedDatabases, SQLDatabases, SQLDatawarehouse, SQLElasticPools,
    SQLManagedInstances, SQLServer, SynapseAnalytics, Timestream
)
```

---

## Storage

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.Storage/storageAccounts` | `diagrams.azure.storage` | `StorageAccounts` |
| `Microsoft.DataLakeStore/accounts` | `diagrams.azure.storage` | `DataLakeStorage` |
| `Microsoft.Storage/storageAccounts/blobServices` | `diagrams.azure.storage` | `BlobStorage` |
| `Microsoft.Storage/storageAccounts/fileServices` | `diagrams.azure.storage` | `FileStorage` |
| `Microsoft.Storage/storageAccounts/tableServices` | `diagrams.azure.storage` | `TableStorage` |
| `Microsoft.Storage/storageAccounts/queueServices` | `diagrams.azure.storage` | `QueuesStorage` |
| `Microsoft.StorageSync/storageSyncServices` | `diagrams.azure.storage` | `StorageSyncServices` |

**All available storage classes:**
```python
from diagrams.azure.storage import (
    ArchiveStorage, BlobStorage, DataBoxEdgeDataBoxGateway, DataBox,
    DataLakeStorage, FileStorage, GeneralStorage, QueuesStorage,
    StorageAccounts, StorageExplorer, StorageSyncServices, TableStorage
)
```

---

## Networking

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.Network/virtualNetworks` | `diagrams.azure.network` | `VirtualNetworks` |
| `Microsoft.Network/loadBalancers` | `diagrams.azure.network` | `LoadBalancers` |
| `Microsoft.Network/applicationGateways` | `diagrams.azure.network` | `ApplicationGateway` |
| `Microsoft.Network/publicIPAddresses` | `diagrams.azure.network` | `PublicIPAddresses` |
| `Microsoft.Network/networkSecurityGroups` | `diagrams.azure.network` | `NetworkSecurityGroups` |
| `Microsoft.Network/dnsZones` | `diagrams.azure.network` | `DNSZones` |
| `Microsoft.Network/privateDnsZones` | `diagrams.azure.network` | `DNSPrivateZones` |
| `Microsoft.Network/frontDoors` | `diagrams.azure.network` | `FrontDoors` |
| `Microsoft.Network/trafficManagerProfiles` | `diagrams.azure.network` | `TrafficManagerProfiles` |
| `Microsoft.Network/expressRouteCircuits` | `diagrams.azure.network` | `ExpressrouteCircuits` |
| `Microsoft.Network/virtualNetworkGateways` | `diagrams.azure.network` | `VirtualNetworkGateways` |
| `Microsoft.Network/localNetworkGateways` | `diagrams.azure.network` | `LocalNetworkGateways` |
| `Microsoft.Network/connections` | `diagrams.azure.network` | `Connections` |
| `Microsoft.Network/azureFirewalls` | `diagrams.azure.network` | `Firewall` |
| `Microsoft.Network/bastionHosts` | `diagrams.azure.security` | `Bastion` |
| `Microsoft.Network/natGateways` | `diagrams.azure.network` | `NATGateway` |
| `Microsoft.Network/routeTables` | `diagrams.azure.network` | `RouteTables` |
| `Microsoft.Network/privateEndpoints` | `diagrams.azure.network` | `PrivateEndpoint` |
| `Microsoft.Network/networkInterfaces` | `diagrams.azure.network` | `NetworkInterfaces` |
| `Microsoft.Network/networkWatchers` | `diagrams.azure.network` | `NetworkWatcher` |
| `Microsoft.Network/ddosProtectionPlans` | `diagrams.azure.network` | `DDOSProtectionPlans` |
| `Microsoft.Cdn/profiles` | `diagrams.azure.network` | `CDNProfiles` |

**All available network classes:**
```python
from diagrams.azure.network import (
    ApplicationGateway, ApplicationSecurityGroups, CDNProfiles, Connections,
    DDOSProtectionPlans, DNSPrivateZones, DNSZones, ExpressrouteCircuits,
    Firewall, FrontDoors, IPGroups, LoadBalancers, LocalNetworkGateways,
    NATGateway, NetworkInterfaces, NetworkSecurityGroups, NetworkWatcher,
    OnPremisesDataGateways, PrivateEndpoint, PublicIPAddresses, RouteFilters,
    RouteTables, ServiceEndpointPolicies, Subnets, TrafficManagerProfiles,
    VirtualNetworkGateways, VirtualNetworks, VirtualWans
)
```

---

## Security

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.KeyVault/vaults` | `diagrams.azure.security` | `KeyVaults` |
| `Microsoft.Network/bastionHosts` | `diagrams.azure.security` | `Bastion` |
| `Microsoft.Sentinel/workspaces` | `diagrams.azure.security` | `Sentinel` |

**All available security classes:**
```python
from diagrams.azure.security import (
    Bastion, ConditionalAccess, Defender, InformationProtection,
    KeyVaults, MicrosoftAntimalware, MicrosoftAzureInformationProtection,
    SecurityCenter, Sentinel
)
```

---

## Integration & Messaging

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.ServiceBus/namespaces` | `diagrams.azure.integration` | `ServiceBus` |
| `Microsoft.EventHub/namespaces` | `diagrams.azure.integration` | `EventHubs` |
| `Microsoft.EventHub/clusters` | `diagrams.azure.integration` | `EventHubClusters` |
| `Microsoft.EventGrid/topics` | `diagrams.azure.integration` | `EventGridTopics` |
| `Microsoft.EventGrid/domains` | `diagrams.azure.integration` | `EventGridDomains` |
| `Microsoft.EventGrid/systemTopics` | `diagrams.azure.integration` | `SystemTopic` |
| `Microsoft.Logic/workflows` | `diagrams.azure.integration` | `LogicApps` |
| `Microsoft.Logic/integrationAccounts` | `diagrams.azure.integration` | `IntegrationAccounts` |
| `Microsoft.ApiManagement/service` | `diagrams.azure.integration` | `APIManagement` |
| `Microsoft.AppConfiguration/configurationStores` | `diagrams.azure.integration` | `AppConfiguration` |
| `Microsoft.Relay/namespaces` | `diagrams.azure.integration` | `Relays` |

**All available integration classes:**
```python
from diagrams.azure.integration import (
    APIForFhir, APIManagement, AppConfiguration, DataCatalog,
    EventGridDomains, EventGridSubscriptions, EventGridTopics,
    EventHubClusters, EventHubs, IntegrationAccounts,
    IntegrationServiceEnvironments, LogicApps, PartnerTopic,
    RelayHybridConnections, Relays, ServiceBus, SystemTopic
)
```

---

## AI & Machine Learning

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.CognitiveServices/accounts` | `diagrams.azure.ml` | `CognitiveServices` |
| `Microsoft.MachineLearningServices/workspaces` | `diagrams.azure.ml` | `MachineLearningServiceWorkspaces` |
| `Microsoft.BotService/botServices` | `diagrams.azure.ml` | `BotServices` |

**All available ML classes:**
```python
from diagrams.azure.ml import (
    BatchAI, BotServices, CognitiveServices, GenomicsAccounts,
    MachineLearningServiceWorkspaces, MachineLearningStudioClassicWebServices,
    MachineLearningStudioClassicWorkspaces
)
```

---

## Analytics / Data

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.Databricks/workspaces` | `diagrams.azure.analytics` | `Databricks` |
| `Microsoft.HDInsight/clusters` | `diagrams.azure.analytics` | `HDInsightClusters` |
| `Microsoft.DataFactory/factories` | `diagrams.azure.analytics` | `DataFactories` |
| `Microsoft.AnalysisServices/servers` | `diagrams.azure.analytics` | `AnalysisServices` |
| `Microsoft.Kusto/clusters` | `diagrams.azure.analytics` | `DataExplorerClusters` |
| `Microsoft.Purview/accounts` | `diagrams.azure.analytics` | `DataCatalog` |
| `Microsoft.StreamAnalytics/streamingJobs` | `diagrams.azure.analytics` | `StreamAnalyticsJobs` |

**All available analytics classes:**
```python
from diagrams.azure.analytics import (
    AnalysisServices, DataExplorerClusters, DataFactories,
    DataLakeAnalytics, DataLakeStoreGen1, Databricks, EventHubClusters,
    EventHubs, HDInsightClusters, LogAnalyticsWorkspaces, StreamAnalyticsJobs
)
```

---

## IoT

| Azure Resource Type | diagrams Module | Class |
|---|---|---|
| `Microsoft.Devices/IotHubs` | `diagrams.azure.iot` | `IotHub` |
| `Microsoft.Devices/provisioningServices` | `diagrams.azure.iot` | `DeviceProvisioningServices` |
| `Microsoft.DigitalTwins/digitalTwinsInstances` | `diagrams.azure.iot` | `DigitalTwins` |

**All available IoT classes:**
```python
from diagrams.azure.iot import (
    DeviceProvisioningServices, DigitalTwins, IotCentral, IotHub,
    IotHubSecurity, Maps, Sphere, TimeSeriesInsightsEnvironments, Windows10IotCoreServices
)
```

---

## General / Fallback

Used automatically for any resource type not in the mapping above:
```python
from diagrams.azure.general import Resourcegroups
```

All available general classes:
```python
from diagrams.azure.general import (
    Allresources, Azurehome, Management, Managementgroups,
    Resourcegroups, Servicehealth, Subscriptions, Tags,
    Templates, Twousericon, Userprivacy, Userresource
)
```

---

## Adding Custom Edges to Generated Diagrams

After running `generate_azure_diagram.py --dump-code`, you can manually add edges.

Common patterns:

```python
# Load balancer → App Services
prod_lb >> [web1, web2, web3]

# App Service → database
web1 >> Edge(label="SQL") >> prod_sql

# VMs → Redis cache
(vm1 - vm2 - vm3) >> Edge(color="brown", style="dashed") >> redis_cache

# API Management → backend services
apim >> Edge(label="routes to") >> web1
apim >> Edge(label="routes to") >> func_app

# AKS cluster
with Cluster("AKS: prod-aks"):
    worker1 = KubernetesServices("node-pool-1")
    worker2 = KubernetesServices("node-pool-2")
```

---

## Querying Azure for Topology Enrichment

```bash
# VNets + subnets
az network vnet list --subscription <id> -o json

# NSG associations
az network nsg list --subscription <id> -o json

# Private DNS links
az network private-dns link vnet list --resource-group <rg> --zone-name <zone> -o json

# App Service outbound connections
az webapp config connection-string list --name <app> --resource-group <rg> -o json

# AKS node pools
az aks nodepool list --resource-group <rg> --cluster-name <aks> -o json

# SQL firewall rules
az sql server firewall-rule list --server <server> --resource-group <rg> -o json
```
