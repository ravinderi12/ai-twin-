# Risk Scoring & Simulation Methodology

## 1. Academic Rationale

Traditional vulnerability scanners (e.g. OpenVAS, Nessus) evaluate security flaws in isolation, generating lengthy static lists of Common Vulnerabilities and Exposures (CVEs) scored strictly by raw CVSS base metrics. This approach introduces severe alert fatigue because it fails to consider:
1. **Topological Reachability**: Is a vulnerable service directly exposed to the public Internet, reachable across internal subnets, or deeply isolated behind access control firewalls?
2. **Multi-Hop Exploit Chaining**: How can an adversary chain multiple low- or medium-severity issues to achieve lateral movement into high-value target assets?
3. **Asset Criticality**: What is the business impact and operational centrality of the affected system within the enterprise?

The **AI-Powered Cybersecurity Digital Twin** solves this by formulating a topology-aware risk analysis engine that quantifies exposure dynamically.

---

## 2. Mathematical Risk Formulation

### A. Context-Aware Finding Risk
For any discovered vulnerability finding $k$ residing on asset $A$, the contextual risk score is quantified as:

$$\text{Contextual\_Risk}(k) = \text{Normalized\_CVSS}(k) \times W_{\text{reach}}(k) \times W_{\text{impact}}(A) \times W_{\text{conf}}(k) \times 100$$

Where:
- $\text{Normalized\_CVSS}(k) = \frac{\text{CVSS}_{\text{base}}(k)}{10.0} \in [0.0, 1.0]$
- $W_{\text{reach}}(k) \in \{1.0, 0.75, 0.30\}$ based on network boundary exposure:
  - `internet_reachable`: $1.0$ (direct external gateway exposure)
  - `subnet_reachable`: $0.75$ (accessible internally across routed subnets)
  - `isolated`: $0.30$ (air-gapped or segmented behind strict egress filters)
- $W_{\text{impact}}(A) = 0.35 + 0.65 \times \left(\frac{\text{ImpactScore}(A)}{100.0}\right) \in [0.35, 1.0]$:
  - Normalizes business impact with a baseline sensitivity floor.
  - Criticality maps to: CRITICAL ($100$), HIGH ($80$), MEDIUM ($50$), LOW ($20$).
- $W_{\text{conf}}(k) \in \{1.0, 0.95, 0.90, 0.85\}$ reflecting telemetry fidelity:
  - `confirmed_signature`: $1.0$ (active probe verification or banner fingerprint)
  - `manual_audit`: $0.95$
  - `simulated_intel`: $0.90$
  - `version_heuristic`: $0.85$ (conservative version match without proof of exploitability)

The resulting score is clamped strictly to $[0.0, 100.0]$.

---

### B. Attack Path Risk (Synopsis Equation)
As specified in **Section 7.2 of the Academic Project Synopsis**, the cumulative risk along an attack trajectory $p$ comprising a sequence of hops is computed as:

$$\text{Risk}(p) = \sum_{k \in \text{path}(p)} \left[\text{CVSS}_{\text{score}}(k) \times \text{Accessibility}_{\text{weight}}(k)\right] \times \text{Impact}(\text{Asset}_{\text{target}})$$

In our implementation, this formula is normalized across the hop count $H$:

$$\text{Path\_Risk}(p) = \min\left(100.0, \frac{\sum_{k \in \text{path}} [\text{CVSS}(k) \times W_{\text{access}}(k)]}{H} \times 10.0 \times \left(\frac{\text{Impact}(\text{Asset}_{\text{target}})}{100.0}\right)\right)$$

This ensures that an exploit located directly on an external-facing perimeter node receives higher prioritization than an identical exploit deep inside an isolated internal subnet.

---

## 3. Graph Pathfinding Algorithms

### Dijkstra's Algorithm (Weighted Adversary Resistance)
Dijkstra's algorithm models the path of least resistance favored by real-world threat actors. Edge weights represent traversal friction:

$$W(u, v) = \max\left(0.2, W_{\text{base}} \times \left(1.0 - \frac{\text{Max\_CVSS}(v)}{20.0}\right)\right)$$

Where higher vulnerability on target system $v$ reduces traversal resistance, making it the preferred lateral hop for simulated adversaries.

### Breadth-First Search (BFS)
BFS explores unweighted minimum-hop trajectories, identifying the shortest traversal depth from an external entry point to internal targets.

---

## 4. Choke Point Identification
To guide patch prioritization, the digital twin computes **network betweenness centrality** $C_B(v)$ across all shortest paths $\sigma_{st}$:

$$C_B(v) = \sum_{s \neq v \neq t} \frac{\sigma_{st}(v)}{\sigma_{st}}$$

Nodes exhibiting peak betweenness centrality are flagged as **critical choke points**. Eliminating vulnerabilities or restricting ingress on these nodes breaks multiple multi-hop attack trajectories simultaneously.
