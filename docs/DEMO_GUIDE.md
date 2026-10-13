# System Demonstration & Evaluation Guide

**Project Title**: AI-Powered Cybersecurity Digital Twin for Vulnerability Assessment and Intelligent Risk Analysis

---

## 1. Quick Startup Instructions

### Step 1: Launch Backend (Terminal 1)
```powershell
# From project root
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend initializes SQLite database and runs at `http://127.0.0.1:8000`. OpenAPI documentation is accessible at `http://127.0.0.1:8000/api/v1/docs`.*

### Step 2: Launch Frontend (Terminal 2)
```powershell
cd frontend
npm run dev
```
*Open your web browser and navigate to `http://localhost:5173`.*

---

## 2. Step-by-Step Viva Demonstration Script

### Act 1: The Core Problem & Motivation (2 Minutes)
1. **Open the SOC Dashboard (`http://localhost:5173`)**:
   - Point out the top header showing: **Cybersecurity Digital Twin // SOC Exposure Suite**.
   - Explain the motivation:
     > *"Conventional scanners like OpenVAS or Nessus treat all vulnerabilities identically based on raw CVSS scores. A CVSS 7.5 flaw on an exposed public server is treated the same as one on an isolated internal machine. Furthermore, active penetration testing on live systems risks service disruption. Our system creates a software-defined digital twin of the network where threat simulations run safely offline with zero production downtime."*

### Act 2: Enterprise Telemetry & Digital Twin Network Map (3 Minutes)
1. **Navigate to "Digital Twin Map"** via the sidebar:
   - Point out the interactive **Cytoscape.js** network canvas.
   - Show the multi-tier enterprise topology:
     - **Ingress Gateway** (`198.51.100.1`)
     - **DMZ Web App** (`192.168.1.10`)
     - **Application Backend** (`192.168.2.20` - Log4j)
     - **Internal Workstation** (`192.168.2.45` - SMBv1)
     - **Customer Database Crown Jewel** (`192.168.3.50` - MySQL)
     - **Active Directory Domain Controller** (`192.168.3.5` - Netlogon)
2. **Click on any node (e.g. `app-srv-01.internal.corp`)**:
   - Show the slide-over inspector drawer displaying open services, ports, and CVE findings.
   - Show how layout options (Concentric, Circle, Force-Directed) and Subnet filters allow an analyst to inspect network boundaries.

### Act 3: Multi-Hop Attack Path Simulation (3 Minutes)
1. **Navigate to "Attack Path Simulator"**:
   - Select **Ingress Node**: `gw-edge-router.corp.net (198.51.100.1)`.
   - Select **Crown Jewel Target**: `db-cust-primary.secure.internal (192.168.3.50)`.
   - Choose Algorithm: **Dijkstra (Weighted Adversary Resistance)**.
   - Click **Run Simulation**.
2. **Review the Results**:
   - Show the visual attack path highlighted in dashed red on the Cytoscape graph!
   - Highlight the **Adversary Narrative**:
     - Hop #1: Ingress through edge router to DMZ Web Portal via port 80.
     - Hop #2: Pivot to backend application server using Spring Boot port 8080.
     - Hop #3: Lateral movement to MySQL database crown jewels on port 3306.
   - Point out the **MITRE ATT&CK Mapping**:
     - `T1190`: Exploit Public-Facing Application (Initial Access)
     - `T1210`: Exploitation of Remote Services (Lateral Movement)
     - `T1565`: Data Manipulation / Database Access (Impact)
   - Highlight the **Identified Choke Point**:
     - Explain how `app-srv-01.internal.corp` acts as a critical topological bottleneck.

### Act 4: Contextual Risk Engine vs CVSS (2 Minutes)
1. **Navigate to "Vulnerability Center"**:
   - Show the comparison table:
     - **Apache CVE-2021-41773** on DMZ Web App: Base CVSS is `7.5`, but its **Context-Aware Risk is elevated to 82.5/100** because it is directly exposed to external ingress!
     - **MySQL CVE-2020-14812** on Internal DB: Base CVSS is `7.1`, but contextual risk is scaled down due to internal subnet segmentation.
   - Click **Inspect Formula** to show the exact breakdown of weights ($W_{\text{reach}}$, $W_{\text{impact}}$, $W_{\text{conf}}$).

### Act 5: Interactive What-If Remediation Sandbox (3 Minutes)
1. **Navigate to "Remediation Planner"**:
   - Point out the ranked worklist prioritizing the choke point flaw (**Log4Shell on App Server**).
   - Show the checkbox selected next to this action.
   - Click **Simulate Proposed Fixes**.
2. **Show the Live What-If Comparison**:
   - The engine clones the digital twin graph into memory.
   - Demonstrates that patching this single vulnerability **BROKE the multi-hop attack path entirely**!
   - Risk reduction: **High percentage decrease**, with zero active paths remaining to the critical crown jewels.
   - Explain to the examiners:
     > *"This demonstrates the core thesis of our project: topology-aware prioritization allows security teams to deploy fewer, more targeted patches that break lateral movement paths, rather than blindly patching hundreds of vulnerabilities."*

### Act 6: Compliance Reports & Downloads (1 Minute)
1. **Navigate to "Compliance Reports"**:
   - Click **Export Findings CSV** to show instant data download.
   - Click **Download Official PDF Assessment Report** to open the publication-grade PDF generated dynamically by Python's ReportLab engine.

---

## 3. Potential Viva Questions & Model Answers

**Q1: How does your risk engine differ from standard CVSS?**  
*Answer: Standard CVSS provides isolated base scores. Our engine implements the formula specified in our synopsis ($Risk(p) = \sum [CVSS(k) \times W_{access}(k)] \times Impact(Asset_{target})$), incorporating network segmentation, reachability from external ingress points, and asset business criticality.*

**Q2: Does your tool execute real exploits against the network?**  
*Answer: Absolutely not. The platform creates a mathematical software replica (Digital Twin) using NetworkX. Simulations use graph traversal algorithms (BFS and Dijkstra) to trace potential lateral movement pathways without running exploit payloads or causing downtime.*

**Q3: How do you identify choke points in the network?**  
*Answer: We calculate network betweenness centrality $C_B(v)$ across all shortest communication paths. Nodes with peak centrality represent topological bottlenecks where a single fix severs multiple multi-hop trajectories.*

**Q4: How is NVD vulnerability data handled offline?**  
*Answer: The backend integrates the official NIST NVD API 2.0 with local SQLite database caching and an authentic offline CVE fallback catalog for air-gapped lab environments.*
