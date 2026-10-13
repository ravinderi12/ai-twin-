# Automated Testing Documentation

## 1. Overview

The testing strategy validates all core tiers of the **AI-Powered Cybersecurity Digital Twin**:
- Application health and readiness checks
- Database persistence and duplicate handling
- Nmap XML parsing and XXE security vulnerability defenses
- Graph synthesis, betweenness centrality, and graph traversal (BFS / Dijkstra)
- Contextual risk formula validation and reachability comparison
- Remediation what-if simulation and delta calculation
- Scanner safety controls and public IP blocking
- Report generation (CSV data export and ReportLab PDF compilation)

---

## 2. Test Execution Command

Run the automated test suite from the repository root:

```powershell
python -m pytest backend/tests -v
```

Or execute the provided batch runner:

```cmd
.\scripts\run_tests.bat
```

---

## 3. Test Suite Inventory

| Test Module | Test Case | Target Verification | Status |
| :--- | :--- | :--- | :--- |
| `test_health.py` | `test_health_endpoint` | Verifies API health status, database connection, and scanner availability | PASSED |
| `test_health.py` | `test_readiness_endpoint` | Confirms Kubernetes/Docker readiness probe response | PASSED |
| `test_health.py` | `test_root_endpoint` | Confirms root API index and OpenAPI documentation URLs | PASSED |
| `test_assets_crud.py` | `test_create_and_read_asset` | Validates asset insertion, duplicate IP rejection, service port mapping, and cascading deletion | PASSED |
| `test_ingestion.py` | `test_parse_valid_nmap_xml` | Ingests real Nmap XML with open ports, services, and script vulnerabilities | PASSED |
| `test_ingestion.py` | `test_reject_malformed_xml` | Rejects unclosed tags and syntax-corrupted XML payloads | PASSED |
| `test_ingestion.py` | `test_reject_xxe_payload` | Validates XXE defense rejecting custom `<!ENTITY>` definitions | PASSED |
| `test_graph_and_traversal.py` | `test_graph_construction_and_traversal` | Validates NetworkX graph construction, Dijkstra pathfinding, BFS traversal, and unreachable node handling | PASSED |
| `test_risk_engine.py` | `test_contextual_risk_comparison_reachable_vs_isolated` | Proves reachable perimeter assets receive significantly higher risk scores than isolated systems | PASSED |
| `test_risk_engine.py` | `test_risk_score_boundary_conditions` | Verifies score clamping strictly between $0.0$ and $100.0$ | PASSED |
| `test_remediation_simulation.py` | `test_remediation_what_if_scenario` | Clones digital twin, simulates patch on choke point, and verifies attack path severing | PASSED |
| `test_reports.py` | `test_csv_report_generation` | Validates compliance CSV stream containing all findings | PASSED |
| `test_reports.py` | `test_pdf_report_generation` | Validates binary ReportLab PDF generation with `%PDF-` header | PASSED |
| `test_scan_safeguards.py` | `test_target_validation_safeguards` | Enforces private CIDR allowlist and rejects public Internet IP scanning | PASSED |

**Total Result**: 14 tests executed, 14 passed (100% pass rate).

---

## 4. Frontend Build Validation

Compile and bundle the React TypeScript frontend:

```powershell
cd frontend
npm run build
```

**Build Outcome**: Clean compilation via TypeScript and Vite into `frontend/dist/` with zero errors.
