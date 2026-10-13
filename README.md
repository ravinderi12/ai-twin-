# AI-Powered Cybersecurity Digital Twin for Vulnerability Assessment and Intelligent Risk Analysis

**Enterprise Vulnerability Assessment, Topological Exposure Quantification & Attack Path Simulation Platform**

---

## 1. Project Overview

Modern enterprise infrastructures are interconnected, dynamic environments where security weaknesses frequently emerge across multiple tiers. Conventional vulnerability assessment tools (such as OpenVAS, Nessus, and Qualys) perform point-in-time signature scanning and rank findings strictly by raw CVSS base severity. This induces severe alert fatigue while failing to reveal how adversaries chain multiple low- or medium-severity weaknesses to move laterally across a network. Furthermore, conducting active penetration testing directly against live production systems introduces risks of crashes and service downtime.

This software project delivers an **AI-Powered Cybersecurity Digital Twin (CDT)** that creates an isolated, software-defined mathematical replica of enterprise networks. By evaluating network reachability, inter-host relationships, and exploit chaining potential entirely within the virtual model, security teams can simulate threat trajectories, quantify context-aware risk, and identify critical network choke points where targeted remediations break multiple lateral attack paths simultaneously.

---

## 2. Core Capabilities & Innovation

- **Non-Intrusive Asset Ingestion**: Ingests network topology from authorized Nmap XML scans, structured JSON schemas, or an offline enterprise demonstration environment.
- **Defensive Data Ingestion**: Secure XML stream parser with built-in XXE (XML External Entity) and entity expansion injection defenses.
- **Mathematical Digital Twin**: NetworkX directed graph representation modeling hosts, open ports, running daemon versions, and inter-subnet routing constraints.
- **Offline Multi-Hop Attack Path Simulation**: Evaluates potential lateral movement trajectories using **Dijkstra's Algorithm** (path of least resistance) and **Breadth-First Search (BFS)** without launching destructive payloads.
- **MITRE ATT&CK Alignment**: Maps simulated actions to standardized tactics and techniques (Initial Access T1190, Lateral Movement T1210/T1021, Privilege Escalation T1068, Impact T1565).
- **Topology-Aware Risk Engine**: Implements the academic synopsis risk formula combining CVSS severity, network reachability, and asset impact weights.
- **Topological Choke Point Discovery**: Calculates network betweenness centrality to pinpoint bottlenecks where a single software patch severs multiple breach paths.
- **Interactive What-If Patch Sandbox**: Clones the digital twin, applies proposed fixes to virtual nodes, recalculates paths, and displays risk reduction delta before any production action is taken.
- **Vulnerability Intelligence Synchronization**: Integrates NIST NVD API 2.0 with local SQLite database caching and an authentic offline fallback catalog.
- **Compliance Reporting**: Exports CSV vulnerability datasets and generates publication-grade PDF assessment audit reports via ReportLab.
- **Professional SOC Web Dashboard**: Dark charcoal interface with cyan/amber/red accents, interactive Cytoscape.js canvas, and real-time metric analytics.

---

## 3. Technology Stack

### Backend
- **Language**: Python 3.9+ / 3.10+
- **Framework**: FastAPI (Asynchronous REST API v1)
- **ASGI Server**: Uvicorn
- **Validation**: Pydantic v2
- **ORM & Persistence**: SQLAlchemy 2.0 with SQLite (`cyber_digital_twin.db`) / PostgreSQL ready
- **Graph Algorithms**: NetworkX 3.2+
- **HTTP Client**: HTTPX 0.28+
- **Reporting**: ReportLab 4.1+ (PDF generation) and standard CSV
- **Testing**: Pytest 8.1+

### Frontend
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS v4 (Dark SOC palette)
- **Graph Canvas**: Cytoscape.js (COSE force-directed, concentric, and circular layouts)
- **Charts**: Recharts
- **Icons**: Lucide React
- **Routing**: React Router v7

---

## 4. Directory Structure

```
project/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point, CORS, and auto-seeding
│   │   ├── core/                    # Settings, JWT security, and configuration
│   │   ├── api/v1/                  # REST v1 API route handlers
│   │   ├── models/                  # SQLAlchemy persistent database models
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── database/                # SQLite engine and session management
│   │   ├── ingestion/               # Nmap XML parser (XXE-safe) and JSON importer
│   │   ├── scanners/                # Safe Nmap scanner runner with allowlists
│   │   ├── digital_twin/            # NetworkX graph synthesis & betweenness centrality
│   │   ├── risk_engine/             # Contextual risk quantification formula
│   │   ├── simulation/              # Attack path simulator & what-if remediation engine
│   │   ├── integrations/            # NIST NVD API 2.0 client & local cache
│   │   ├── services/                # PDF (ReportLab) and CSV report generators
│   │   └── sample_data/             # Multi-tier enterprise topology seeder
│   ├── tests/                       # Pytest test suite (14 automated tests)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/              # Navbar, Sidebar, CytoscapeGraph, StatCards, Badges
│   │   ├── pages/                   # Overview, Topology, Simulation, Remediation, Assets, Vulns, Scans, CVE, Reports
│   │   ├── services/                # Axios API client functions
│   │   ├── types/                   # TypeScript interfaces
│   │   ├── App.tsx                  # Main router and SOC layout
│   │   └── index.css                # Dark SOC theme styles
│   ├── package.json
│   └── vite.config.ts
├── sample_data/                     # Sample Nmap XML, JSON, and malicious XXE test fixtures
├── docs/                            # Architecture, Schema, Methodology, Testing, and Demo guides
├── scripts/                         # One-click Windows startup batch scripts
├── README.md
└── .gitignore
```

---

## 5. Getting Started & Installation

### Prerequisites
- Python 3.9+ or 3.10+
- Node.js v18+ and npm
- (Optional) Nmap on PATH for live local scans

### Backend Setup
1. Open a terminal in the project directory:
   ```powershell
   python -m pip install -r backend/requirements.txt
   ```
2. Verify environment configuration:
   - A default `.env` file is pre-configured with secure offline defaults.
3. Start the FastAPI backend:
   ```powershell
   python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   *The database schema initializes automatically, and the enterprise demo topology seeds on initial run.*

### Frontend Setup
1. Open a second terminal:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
2. Open your browser and navigate to:
   ```
   http://localhost:5173
   ```

---

## 6. Running Automated Tests

Execute the complete 14-test verification suite:

```powershell
python -m pytest backend/tests -v
```

All 14 tests validate:
- System startup and health checks
- Asset CRUD operations and duplicate prevention
- Secure Nmap XML parsing & XXE payload rejection
- NetworkX graph synthesis, BFS, Dijkstra, and unreachable nodes
- Contextual risk formula validation (perimeter vs isolated asset delta)
- Remediation what-if simulation & path severing
- Scanner safety boundaries and public IP rejection
- Compliance CSV export and ReportLab binary PDF generation

---

## 7. Safety Boundaries & Security Controls

- **Zero Exploits**: Simulations operate exclusively on the software graph model. No active exploit payloads, memory corruption attacks, or credential theft attempts are executed against live devices.
- **Scanner Target Constraints**: Live scans are restricted to RFC1918 private subnets and localhost (`127.0.0.1`). Public Internet ranges are blocked by default.
- **No Command Injection**: Scanner execution uses strict subprocess argument arrays without shell interpolation (`shell=False`).
- **XXE Hardening**: XML parsing prohibits inline entity definitions (`<!ENTITY>`) and external DTD references.

---

## 8. Academic Documentation

- [System Architecture](docs/ARCHITECTURE.md)
- [Database Schema](docs/DATABASE_SCHEMA.md)
- [Risk Scoring Methodology](docs/RISK_METHODOLOGY.md)
- [Automated Testing Report](docs/TESTING.md)
- [College Viva Demonstration Guide](docs/DEMO_GUIDE.md)

---

## 9. License & Classification

Internal Security Assessment & Research Platform. All rights reserved.
