import json
from sqlalchemy.orm import Session
from backend.app.models.models import (
    Asset, ServicePort, NetworkRelationship, Assessment,
    VulnerabilityFinding, RemediationRecommendation
)

SAMPLE_ASSETS = [
    {
        "hostname": "gw-edge-router.corp.net",
        "ip_address": "198.51.100.1",
        "mac_address": "52:54:00:12:34:01",
        "os_name": "Cisco IOS-XE / Linux Embedded",
        "os_version": "17.3",
        "asset_type": "gateway",
        "criticality": "HIGH",
        "environment": "external",
        "subnet": "198.51.100.0/24",
        "is_isolated": False,
        "is_perimeter": True,
        "business_impact_score": 75.0,
        "notes": "External perimeter router forwarding incoming HTTP/S traffic to DMZ.",
        "services": [
            {"port": 80, "protocol": "tcp", "service_name": "http", "product": "Edge Proxy", "version": "1.2", "state": "open"},
            {"port": 443, "protocol": "tcp", "service_name": "https", "product": "Edge Proxy SSL", "version": "1.2", "state": "open"},
            {"port": 22, "protocol": "tcp", "service_name": "ssh", "product": "OpenSSH", "version": "8.0", "state": "open"}
        ]
    },
    {
        "hostname": "dmz-web-app.enterprise.local",
        "ip_address": "192.168.1.10",
        "mac_address": "52:54:00:12:34:02",
        "os_name": "Ubuntu Linux",
        "os_version": "20.04 LTS",
        "asset_type": "server",
        "criticality": "HIGH",
        "environment": "dmz",
        "subnet": "192.168.1.0/24",
        "is_isolated": False,
        "is_perimeter": True,
        "business_impact_score": 70.0,
        "notes": "Public-facing customer e-commerce web application reverse proxy.",
        "services": [
            {"port": 80, "protocol": "tcp", "service_name": "http", "product": "Apache httpd", "version": "2.4.49", "state": "open"},
            {"port": 443, "protocol": "tcp", "service_name": "https", "product": "Apache httpd", "version": "2.4.49", "state": "open"},
            {"port": 22, "protocol": "tcp", "service_name": "ssh", "product": "OpenSSH", "version": "8.2p1", "state": "open"}
        ],
        "findings": [
            {
                "cve_id": "CVE-2021-41773",
                "title": "[SIMULATED LAB] Apache HTTP Server 2.4.49 Path Traversal & Remote Code Execution",
                "description": "A flaw was found in a change made to path normalization in Apache HTTP Server 2.4.49. An attacker could map URLs to files outside the expected document root.",
                "cvss_v3_score": 7.5,
                "cvss_v3_severity": "HIGH",
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
                "reference_url": "https://nvd.nist.gov/vuln/detail/CVE-2021-41773",
                "source": "Simulated Threat Feed",
                "match_type": "version_heuristic",
                "reachability_status": "internet_reachable",
                "raw_score": 75.0,
                "contextual_risk_score": 82.5,
                "remediation_advice": "Upgrade Apache HTTP Server to version 2.4.51 or later immediately."
            }
        ]
    },
    {
        "hostname": "app-srv-01.internal.corp",
        "ip_address": "192.168.2.20",
        "mac_address": "52:54:00:12:34:03",
        "os_name": "Red Hat Enterprise Linux",
        "os_version": "8.4",
        "asset_type": "server",
        "criticality": "HIGH",
        "environment": "internal",
        "subnet": "192.168.2.0/24",
        "is_isolated": False,
        "is_perimeter": False,
        "business_impact_score": 85.0,
        "notes": "Core backend middleware API processing orders and communicating with database.",
        "services": [
            {"port": 8080, "protocol": "tcp", "service_name": "http-alt", "product": "Java Spring Boot / Log4j", "version": "2.14.1", "state": "open"},
            {"port": 22, "protocol": "tcp", "service_name": "ssh", "product": "OpenSSH", "version": "8.0", "state": "open"}
        ],
        "findings": [
            {
                "cve_id": "CVE-2021-44228",
                "title": "[SIMULATED LAB] Apache Log4j2 JNDI Remote Code Execution (Log4Shell)",
                "description": "Apache Log4j2 2.0-beta9 through 2.15.0 JNDI features do not protect against attacker-controlled LDAP and other JNDI related endpoints, allowing unauthenticated RCE.",
                "cvss_v3_score": 10.0,
                "cvss_v3_severity": "CRITICAL",
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                "reference_url": "https://nvd.nist.gov/vuln/detail/CVE-2021-44228",
                "source": "Simulated Threat Feed",
                "match_type": "version_heuristic",
                "reachability_status": "subnet_reachable",
                "raw_score": 100.0,
                "contextual_risk_score": 96.0,
                "remediation_advice": "Update log4j-core dependency to 2.17.1 or set log4j2.formatMsgNoLookups=true system property."
            }
        ]
    },
    {
        "hostname": "ws-hr-alice.internal.corp",
        "ip_address": "192.168.2.45",
        "mac_address": "52:54:00:12:34:04",
        "os_name": "Microsoft Windows 10 Pro",
        "os_version": "1909",
        "asset_type": "workstation",
        "criticality": "MEDIUM",
        "environment": "internal",
        "subnet": "192.168.2.0/24",
        "is_isolated": False,
        "is_perimeter": False,
        "business_impact_score": 45.0,
        "notes": "Internal user workstation in Human Resources subnet.",
        "services": [
            {"port": 445, "protocol": "tcp", "service_name": "microsoft-ds", "product": "Microsoft Windows SMB", "version": "SMBv1", "state": "open"},
            {"port": 3389, "protocol": "tcp", "service_name": "ms-wbt-server", "product": "Microsoft Terminal Services", "version": "10.0", "state": "open"}
        ],
        "findings": [
            {
                "cve_id": "CVE-2017-0144",
                "title": "[SIMULATED LAB] Microsoft SMBv1 Remote Code Execution (EternalBlue)",
                "description": "A remote code execution vulnerability exists in Microsoft Server Message Block 1.0 (SMBv1) protocol when handling specially crafted packets.",
                "cvss_v3_score": 8.1,
                "cvss_v3_severity": "HIGH",
                "cvss_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
                "reference_url": "https://nvd.nist.gov/vuln/detail/CVE-2017-0144",
                "source": "Simulated Threat Feed",
                "match_type": "version_heuristic",
                "reachability_status": "subnet_reachable",
                "raw_score": 81.0,
                "contextual_risk_score": 68.5,
                "remediation_advice": "Apply Microsoft Security Bulletin MS17-010 and disable SMBv1 feature."
            }
        ]
    },
    {
        "hostname": "db-cust-primary.secure.internal",
        "ip_address": "192.168.3.50",
        "mac_address": "52:54:00:12:34:05",
        "os_name": "Debian GNU/Linux",
        "os_version": "11 (bullseye)",
        "asset_type": "database",
        "criticality": "CRITICAL",
        "environment": "internal",
        "subnet": "192.168.3.0/24",
        "is_isolated": False,
        "is_perimeter": False,
        "business_impact_score": 95.0,
        "notes": "Primary relational database storing customer financial records and PII.",
        "services": [
            {"port": 3306, "protocol": "tcp", "service_name": "mysql", "product": "MySQL Server", "version": "5.7.30", "state": "open"},
            {"port": 22, "protocol": "tcp", "service_name": "ssh", "product": "OpenSSH", "version": "8.4p1", "state": "open"}
        ],
        "findings": [
            {
                "cve_id": "CVE-2020-14812",
                "title": "[SIMULATED LAB] Oracle MySQL Server Optimizer Component Vulnerability",
                "description": "Vulnerability in the MySQL Server product of Oracle MySQL. Easily exploitable vulnerability allows low privileged attacker with network access to compromise MySQL Server.",
                "cvss_v3_score": 7.1,
                "cvss_v3_severity": "HIGH",
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N",
                "reference_url": "https://nvd.nist.gov/vuln/detail/CVE-2020-14812",
                "source": "Simulated Threat Feed",
                "match_type": "version_heuristic",
                "reachability_status": "isolated",
                "raw_score": 71.0,
                "contextual_risk_score": 79.8,
                "remediation_advice": "Upgrade MySQL Server to 5.7.32 or 8.0.22 and enforce strict subnet ingress filtering."
            }
        ]
    },
    {
        "hostname": "dc01-ad.secure.internal",
        "ip_address": "192.168.3.5",
        "mac_address": "52:54:00:12:34:06",
        "os_name": "Microsoft Windows Server 2019",
        "os_version": "1809",
        "asset_type": "server",
        "criticality": "CRITICAL",
        "environment": "management",
        "subnet": "192.168.3.0/24",
        "is_isolated": False,
        "is_perimeter": False,
        "business_impact_score": 100.0,
        "notes": "Central Active Directory Domain Controller and Kerberos Key Distribution Center.",
        "services": [
            {"port": 88, "protocol": "tcp", "service_name": "kerberos", "product": "Microsoft Kerberos", "version": "KDC", "state": "open"},
            {"port": 389, "protocol": "tcp", "service_name": "ldap", "product": "Microsoft Active Directory LDAP", "version": "AD LDS", "state": "open"},
            {"port": 445, "protocol": "tcp", "service_name": "microsoft-ds", "product": "Microsoft Windows SMB", "version": "SMBv2/v3", "state": "open"}
        ],
        "findings": [
            {
                "cve_id": "CVE-2020-1472",
                "title": "[SIMULATED LAB] Netlogon Elevation of Privilege (Zerologon)",
                "description": "An elevation of privilege vulnerability exists when an attacker establishes a vulnerable Netlogon secure channel connection to a domain controller using the Netlogon Remote Protocol (MS-NRPC).",
                "cvss_v3_score": 10.0,
                "cvss_v3_severity": "CRITICAL",
                "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
                "reference_url": "https://nvd.nist.gov/vuln/detail/CVE-2020-1472",
                "source": "Simulated Threat Feed",
                "match_type": "version_heuristic",
                "reachability_status": "subnet_reachable",
                "raw_score": 100.0,
                "contextual_risk_score": 98.5,
                "remediation_advice": "Deploy Microsoft Security Update KB4557222 and enforce secure RPC on all domain-joined machines."
            }
        ]
    }
]

# Topology relationships: (source_ip, target_ip, relationship_type, port, confidence, weight, description)
SAMPLE_RELATIONSHIPS = [
    ("198.51.100.1", "192.168.1.10", "routes_to", 80, "HIGH", 1.0, "Perimeter reverse proxy routing external web traffic to DMZ portal"),
    ("198.51.100.1", "192.168.1.10", "routes_to", 443, "HIGH", 1.0, "Perimeter SSL termination forwarding to DMZ portal"),
    ("192.168.1.10", "192.168.2.20", "can_connect", 8080, "HIGH", 1.2, "DMZ frontend connecting to internal backend Spring Boot REST API"),
    ("192.168.2.20", "192.168.3.50", "can_connect", 3306, "HIGH", 1.1, "Application backend communicating directly with MySQL database"),
    ("192.168.2.20", "192.168.3.5", "can_connect", 389, "HIGH", 1.5, "App Server querying Active Directory for user directory authentication"),
    ("192.168.2.45", "192.168.2.20", "can_connect", 8080, "MEDIUM", 1.8, "Internal user workstation accessing internal business app portal"),
    ("192.168.2.45", "192.168.3.5", "can_connect", 88, "HIGH", 1.0, "Workstation domain authentication with Active Directory KDC")
]

def load_sample_topology(db: Session, force_reload: bool = False) -> Assessment:
    """
    Seeds or re-seeds the fictional enterprise network digital twin into the database.
    Returns the created demonstration assessment record.
    """
    if force_reload:
        db.query(RemediationRecommendation).delete()
        db.query(VulnerabilityFinding).delete()
        db.query(NetworkRelationship).delete()
        db.query(ServicePort).delete()
        db.query(Asset).delete()
        db.query(Assessment).filter(Assessment.assessment_type == "simulated_demo").delete()
        db.commit()

    # Create assessment record
    assessment = Assessment(
        title="Simulated Enterprise Cyber Range Audit",
        description="Fictional multi-tiered corporate network demonstration demonstrating perimeter DMZ, application tier, customer database crown jewels, and Active Directory domain controller.",
        assessment_type="simulated_demo",
        target_scope="198.51.100.0/24, 192.168.1.0/24, 192.168.2.0/24, 192.168.3.0/24",
        status="completed",
        total_assets_found=len(SAMPLE_ASSETS),
        total_vulns_found=sum(len(a.get("findings", [])) for a in SAMPLE_ASSETS),
        overall_risk_score=78.4,
        execution_duration_seconds=2.45
    )
    db.add(assessment)
    db.flush()

    ip_to_asset_id = {}

    for asset_dict in SAMPLE_ASSETS:
        asset = Asset(
            hostname=asset_dict["hostname"],
            ip_address=asset_dict["ip_address"],
            mac_address=asset_dict.get("mac_address"),
            os_name=asset_dict.get("os_name"),
            os_version=asset_dict.get("os_version"),
            asset_type=asset_dict.get("asset_type", "server"),
            criticality=asset_dict.get("criticality", "MEDIUM"),
            environment=asset_dict.get("environment", "internal"),
            subnet=asset_dict.get("subnet"),
            is_isolated=asset_dict.get("is_isolated", False),
            is_perimeter=asset_dict.get("is_perimeter", False),
            business_impact_score=asset_dict.get("business_impact_score", 50.0),
            notes=asset_dict.get("notes")
        )
        db.add(asset)
        db.flush()
        ip_to_asset_id[asset.ip_address] = asset.id

        service_map = {}
        for s_dict in asset_dict.get("services", []):
            service = ServicePort(
                asset_id=asset.id,
                port=s_dict["port"],
                protocol=s_dict.get("protocol", "tcp"),
                service_name=s_dict.get("service_name"),
                product=s_dict.get("product"),
                version=s_dict.get("version"),
                state=s_dict.get("state", "open"),
                is_exposed=True
            )
            db.add(service)
            db.flush()
            service_map[s_dict["port"]] = service.id

        for f_dict in asset_dict.get("findings", []):
            service_id = None
            if f_dict["cve_id"] == "CVE-2021-41773":
                service_id = service_map.get(80)
            elif f_dict["cve_id"] == "CVE-2021-44228":
                service_id = service_map.get(8080)
            elif f_dict["cve_id"] == "CVE-2017-0144":
                service_id = service_map.get(445)
            elif f_dict["cve_id"] == "CVE-2020-14812":
                service_id = service_map.get(3306)
            elif f_dict["cve_id"] == "CVE-2020-1472":
                service_id = service_map.get(445)

            finding = VulnerabilityFinding(
                assessment_id=assessment.id,
                asset_id=asset.id,
                service_id=service_id,
                cve_id=f_dict["cve_id"],
                title=f_dict["title"],
                description=f_dict["description"],
                cvss_v3_score=f_dict["cvss_v3_score"],
                cvss_v3_severity=f_dict["cvss_v3_severity"],
                cvss_vector=f_dict.get("cvss_vector"),
                reference_url=f_dict.get("reference_url"),
                source=f_dict.get("source", "Simulated Threat Feed"),
                match_type=f_dict.get("match_type", "version_heuristic"),
                reachability_status=f_dict.get("reachability_status", "subnet_reachable"),
                raw_score=f_dict.get("raw_score", 70.0),
                contextual_risk_score=f_dict.get("contextual_risk_score", 75.0),
                risk_factors_json=json.dumps({
                    "reachability_weight": 0.9 if asset.is_perimeter else 0.7,
                    "asset_impact_weight": asset.business_impact_score / 100.0,
                    "evidence_confidence": 0.85,
                    "cvss_normalized": f_dict["cvss_v3_score"] / 10.0
                }),
                remediation_advice=f_dict.get("remediation_advice")
            )
            db.add(finding)
            db.flush()

            # Seed ranked remediation
            priority = "CRITICAL" if finding.cvss_v3_score >= 9.0 else "HIGH"
            db.add(RemediationRecommendation(
                assessment_id=assessment.id,
                finding_id=finding.id,
                asset_id=asset.id,
                title=f"Patch {finding.cve_id} on {asset.hostname}",
                action_description=finding.remediation_advice or "Apply latest vendor security patch.",
                priority=priority,
                status="PLANNED",
                risk_before=finding.contextual_risk_score,
                risk_after=finding.contextual_risk_score * 0.25,
                risk_reduction_estimate=finding.contextual_risk_score * 0.75,
                affected_attack_paths_count=2 if "dmz" in asset.environment or "app" in asset.hostname else 1,
                expected_security_benefit=f"Severely restricts lateral movement into {asset.environment} and protects downstream internal assets.",
                notes="Demonstration recommendation generated automatically."
            ))

    # Add network relationships
    for src_ip, tgt_ip, rel_type, port, conf, weight, desc in SAMPLE_RELATIONSHIPS:
        src_id = ip_to_asset_id.get(src_ip)
        tgt_id = ip_to_asset_id.get(tgt_ip)
        if src_id and tgt_id:
            rel = NetworkRelationship(
                source_asset_id=src_id,
                target_asset_id=tgt_id,
                relationship_type=rel_type,
                protocol="tcp",
                port=port,
                is_inferred=False,
                confidence=conf,
                weight=weight,
                description=desc
            )
            db.add(rel)

    db.commit()
    db.refresh(assessment)
    return assessment
