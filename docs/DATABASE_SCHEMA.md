# Database Schema Documentation

The application utilizes SQLAlchemy ORM with a persistent SQLite storage backend (`cyber_digital_twin.db`), designed to seamlessly port to PostgreSQL in enterprise environments.

---

## 1. Table Definitions

### `assets`
Stores discovered or imported enterprise devices and hosts.
- `id` (INTEGER, PK): Unique asset identifier.
- `hostname` (VARCHAR): DNS or NetBIOS host name.
- `ip_address` (VARCHAR, INDEX): IPv4 address.
- `mac_address` (VARCHAR): Physical hardware address.
- `os_name` (VARCHAR): Operating system name.
- `os_version` (VARCHAR): OS build/version.
- `asset_type` (VARCHAR): `server`, `workstation`, `gateway`, `database`, `firewall`.
- `criticality` (VARCHAR): `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- `environment` (VARCHAR): `dmz`, `internal`, `management`, `cloud`, `external`.
- `subnet` (VARCHAR): Network subnet CIDR (e.g. `192.168.1.0/24`).
- `is_perimeter` (BOOLEAN): True if directly exposed to external traffic.
- `is_isolated` (BOOLEAN): True if segmented / air-gapped.
- `business_impact_score` (FLOAT): Relative asset value (1.0 to 100.0).
- `created_at` / `updated_at` (DATETIME): Timestamps.

### `service_ports`
Stores open network sockets, protocols, and daemon version banners.
- `id` (INTEGER, PK): Primary key.
- `asset_id` (INTEGER, FK -> `assets.id` ON DELETE CASCADE): Host reference.
- `port` (INTEGER): Port number (e.g. 80, 443, 3306, 445).
- `protocol` (VARCHAR): `tcp`, `udp`.
- `service_name` (VARCHAR): Standard service (http, ssh, mysql).
- `product` (VARCHAR): Software product (Apache, OpenSSH, MySQL).
- `version` (VARCHAR): Version string (2.4.49, 8.2p1).
- `banner` (TEXT): Service banner or extra probe information.
- `state` (VARCHAR): `open`, `filtered`, `closed`.
- `is_exposed` (BOOLEAN): Exposure flag.

### `network_relationships`
Represents communication pathways between assets forming the topology edges.
- `id` (INTEGER, PK): Relationship identifier.
- `source_asset_id` (INTEGER, FK -> `assets.id`): Source node.
- `target_asset_id` (INTEGER, FK -> `assets.id`): Target node.
- `relationship_type` (VARCHAR): `can_connect`, `routes_to`, `manages`, `trusts`.
- `protocol` (VARCHAR): Connection protocol (`tcp`).
- `port` (INTEGER): Specific target port.
- `is_inferred` (BOOLEAN): True if discovered heuristically.
- `confidence` (VARCHAR): `HIGH`, `MEDIUM`, `LOW`.
- `weight` (FLOAT): Base network traversal friction cost.
- `description` (VARCHAR): Relationship explanation.

### `vulnerability_findings`
Represents identified vulnerabilities mapped to assets and services.
- `id` (INTEGER, PK): Finding ID.
- `assessment_id` (INTEGER, FK -> `assessments.id`): Assessment reference.
- `asset_id` (INTEGER, FK -> `assets.id`): Affected device.
- `service_id` (INTEGER, FK -> `service_ports.id`): Affected service.
- `cve_id` (VARCHAR): Official CVE identifier (e.g. `CVE-2021-44228`).
- `title` (VARCHAR): Advisory title.
- `description` (TEXT): Flaw description.
- `cvss_v3_score` (FLOAT): Raw CVSS base metric (0.0 to 10.0).
- `cvss_v3_severity` (VARCHAR): `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- `cvss_vector` (VARCHAR): Complete CVSS 3.1 vector string.
- `reachability_status` (VARCHAR): `internet_reachable`, `subnet_reachable`, `isolated`.
- `raw_score` (FLOAT): Normalized base score ($CVSS \times 10$).
- `contextual_risk_score` (FLOAT): Topology-aware calculated risk ($0.0$ to $100.0$).
- `risk_factors_json` (TEXT): JSON breakdown of weights and factors.
- `remediation_advice` (TEXT): Recommended mitigation instructions.

### `simulated_attack_paths`
Records executed attack path simulations.
- `id` (INTEGER, PK): Record identifier.
- `assessment_id` (INTEGER, FK): Assessment reference.
- `name` (VARCHAR): Simulation run title.
- `start_asset_id` (INTEGER, FK): Ingress node.
- `target_asset_id` (INTEGER, FK): Crown jewel target.
- `algorithm_used` (VARCHAR): `BFS` or `Dijkstra`.
- `total_path_cost` (FLOAT): Cumulative graph weight.
- `hop_count` (INTEGER): Number of lateral hops.
- `total_path_risk` (FLOAT): Calculated path exposure ($0.0$ to $100.0$).
- `path_nodes_json` (TEXT): Ordered asset IDs.
- `path_steps_json` (TEXT): Full step-by-step traversal narrative.
- `mitre_tactics_json` (TEXT): Mapped MITRE ATT&CK techniques.
- `bottleneck_asset_id` (INTEGER): Identified choke point node.

### `remediation_recommendations`
Stores prioritized remediation worklist items.
- `id` (INTEGER, PK): Work item ID.
- `finding_id` (INTEGER, FK): Targeted vulnerability finding.
- `asset_id` (INTEGER, FK): Target host.
- `title` (VARCHAR): Action title.
- `action_description` (TEXT): Implementation details.
- `priority` (VARCHAR): `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`.
- `status` (VARCHAR): `PLANNED`, `IN_PROGRESS`, `RESOLVED`.
- `risk_before` (FLOAT): Contextual risk prior to fix.
- `risk_after` (FLOAT): Projected risk following fix.
- `risk_reduction_estimate` (FLOAT): Projected risk decrease.
- `affected_attack_paths_count` (INTEGER): Number of lateral paths disrupted.

### `remediation_scenarios`
Stores what-if simulation scenario outcomes.
- `id` (INTEGER, PK): Scenario ID.
- `name` (VARCHAR): Scenario title.
- `baseline_risk_score` (FLOAT): Pre-mitigation path risk.
- `simulated_risk_score` (FLOAT): Post-mitigation path risk.
- `risk_reduction_percentage` (FLOAT): Percentage risk reduction.
- `eliminated_paths_count` (INTEGER): Number of severed paths.
- `patches_applied_json` (TEXT): List of simulated patches applied.

### `cve_cache`
Caches responses from the official NIST NVD API 2.0.
- `cve_id` (VARCHAR, PK): CVE identifier.
- `title` (VARCHAR): Title summary.
- `description` (TEXT): Full description.
- `cvss_v3_score` (FLOAT): Base metric.
- `cvss_v3_severity` (VARCHAR): Severity string.
- `cvss_vector` (VARCHAR): Vector string.
- `published_date` / `last_modified_date` (VARCHAR): Timestamps.
- `reference_urls_json` (TEXT): Authoritative URLs.
- `cached_at` (DATETIME): Local cache time.
