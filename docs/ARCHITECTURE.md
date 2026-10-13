# System Architecture: AI-Powered Cybersecurity Digital Twin

## 1. Architectural Overview

The **AI-Powered Cybersecurity Digital Twin** operates as a modular four-tier architecture designed to replicate real-world enterprise network architectures safely within an analytical, graph-based digital environment without touching active production operations.

```
+-----------------------------------------------------------------------------------+
|                        PRESENTATION & APPLICATION LAYER                           |
|      React 19 + TypeScript + Vite + Tailwind CSS + Cytoscape.js + Recharts        |
+-----------------------------------------------------------------------------------+
                                        | (REST APIs via JSON)
+-----------------------------------------------------------------------------------+
|                           BACKEND API & SECURITY LAYER                            |
|             FastAPI v1 Endpoints (Health, Assets, Simulator, Remediation)          |
+-----------------------------------------------------------------------------------+
       |                                |                             |
+---------------+              +--------------------+         +--------------------+
|  INGESTION &  |              |   DIGITAL TWIN     |         |   AI SIMULATION &  |
|  DISCOVERY    |              |   TOPOLOGY ENGINE  |         |   RISK ENGINE      |
|---------------|              |--------------------|         |--------------------|
| - Nmap XML    |              | - NetworkX DiGraph |         | - BFS & Dijkstra   |
|   Parser (XXE)|              | - Betweenness      |         | - Lateral Pathing  |
| - JSON Schema |              |   Centrality       |         | - Contextual Risk  |
| - Safe Nmap   |              | - Choke Points     |         | - What-If Sandbox  |
|   Subprocess  |              | - Cytoscape Export |         | - MITRE ATT&CK     |
+---------------+              +--------------------+         +--------------------+
       |                                |                             |
+-----------------------------------------------------------------------------------+
|                          PERSISTENCE & INTELLIGENCE LAYER                         |
|     SQLAlchemy ORM + SQLite / PostgreSQL + NVD API 2.0 Client + ReportLab PDF     |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Functional Layers

### Layer 1: Ingestion & Telemetry Parser
- **Nmap XML Parser (`backend/app/ingestion/nmap_parser.py`)**: Secure XML stream parsing that rejects inline entity expansions (`<!ENTITY`), external DTD references (`SYSTEM`/`PUBLIC`), and entity bombs. Extracts active IPv4/MAC addresses, open ports, running services, banner details, and NSE script output.
- **JSON Topology Importer (`backend/app/ingestion/json_importer.py`)**: Ingests normalized multi-asset inventories and explicit network communication pathways.
- **Safe Scanner (`backend/app/scanners/nmap_scanner.py`)**: Validates targets against strict RFC1918 private CIDR allowlists. Rejects public Internet addresses. Requires explicit operator confirmation. Launches subprocesses using safe argument arrays without shell interpolation.

### Layer 2: Digital Twin Graph Engine
- **Mathematical Graph Model (`backend/app/digital_twin/graph_builder.py`)**: Constructs a directed graph $G = (V, E)$ using NetworkX.
  - **Vertices $V$**: Network assets enriched with attributes (operating system, criticality, business impact score, open ports, associated CVEs, perimeter flag).
  - **Edges $E$**: Validated communication channels with weights computed as attacker friction:
    $$W(e) = \max\left(0.2, W_{\text{base}} \times \left(1.0 - \frac{\text{CVSS}_{\text{target}}}{20.0}\right)\right)$$
  - **Bottleneck Analysis**: Identifies critical topological bottlenecks via network betweenness centrality $C_B(v)$.

### Layer 3: Simulation & Risk Engine
- **Graph Traversal (`backend/app/simulation/attack_simulator.py`)**: Evaluates multi-hop lateral movement from an ingress asset to internal crown jewels using Breadth-First Search (minimum hops) and Dijkstra's algorithm (lowest attacker resistance).
- **Taxonomy Mapping**: Maps simulation steps to standardized MITRE ATT&CK techniques:
  - `T1190`: Exploit Public-Facing Application (Initial Access)
  - `T1210`: Exploitation of Remote Services (Lateral Movement)
  - `T1021.004`: SSH Remote Services
  - `T1021.002`: SMB Remote Services
  - `T1558`: Steal / Forge Kerberos Tickets (Credential Access)
  - `T1068`: Exploitation for Privilege Escalation
  - `T1565`: Data Manipulation / Database Access (Impact)
- **What-If Sandbox (`backend/app/simulation/remediation_engine.py`)**: Clones the active digital twin graph, simulates security patches or firewall blocks, and recalculates risk delta and eliminated attack paths.

### Layer 4: Intelligence & Presentation
- **NVD API 2.0 Client (`backend/app/integrations/nvd_client.py`)**: Fetches authentic CVE descriptions, CVSS v3.1 metrics, and reference URLs with SQLite database caching and offline fallback.
- **PDF Report Engine (`backend/app/services/report_generator.py`)**: Generates formal PDF audit reports via ReportLab.
- **React SOC Web Dashboard**: Interactive Cytoscape.js canvas, Recharts trend metrics, and real-time what-if scenario testing.
