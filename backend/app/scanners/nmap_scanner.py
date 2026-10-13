import ipaddress
import shutil
import subprocess
import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.ingestion.nmap_parser import NmapXMLParser
from backend.app.models.models import Assessment, Asset, ServicePort, AuditEvent

class ScannerSafetyError(Exception):
    pass

class NmapScannerService:
    """
    Safely executes local discovery sweeps within authorized ranges.
    Adheres to strict security boundaries: no arbitrary arguments, no shell execution,
    strict CIDR allowlists, operator authorization confirmation required.
    """

    @classmethod
    def is_nmap_available(cls) -> bool:
        return shutil.which(settings.NMAP_PATH) is not None

    @classmethod
    def validate_target(cls, target_str: str) -> None:
        """
        Validates target IP or CIDR against ALLOWED_SCAN_RANGES.
        Rejects public Internet IPs by default unless specifically allowed in config.
        """
        allowed_networks = []
        for net_str in settings.ALLOWED_SCAN_RANGES.split(","):
            net_str = net_str.strip()
            if net_str:
                try:
                    if "/" in net_str:
                        allowed_networks.append(ipaddress.ip_network(net_str, strict=False))
                    else:
                        allowed_networks.append(ipaddress.ip_network(f"{net_str}/32", strict=False))
                except ValueError:
                    continue

        # Parse given target
        target_str = target_str.strip()
        try:
            if "/" in target_str:
                target_net = ipaddress.ip_network(target_str, strict=False)
            else:
                target_net = ipaddress.ip_network(f"{target_str}/32", strict=False)
        except ValueError:
            raise ScannerSafetyError(f"Invalid target format: '{target_str}'. Must be a valid IPv4 address or CIDR notation.")

        # Check if target is private or loopback
        if not (target_net.is_private or target_net.is_loopback):
            raise ScannerSafetyError(f"Target '{target_str}' is a public Internet range. Live scanning of public ranges is prohibited.")

        # Check if target is covered by allowed CIDR ranges
        is_allowed = any(target_net.subnet_of(allowed) for allowed in allowed_networks)
        if not is_allowed:
            raise ScannerSafetyError(f"Target '{target_str}' is outside configured authorized scope: {settings.ALLOWED_SCAN_RANGES}")

    @classmethod
    def execute_authorized_scan(
        cls,
        db: Session,
        target: str,
        scan_type: str,
        confirm_authorized: bool,
        operator_username: str = "security_analyst",
        operator_ip: str = "127.0.0.1"
    ) -> Assessment:
        if not confirm_authorized:
            raise ScannerSafetyError("Operator must explicitly confirm authorization before initiating a live scan.")

        if not settings.ENABLE_LIVE_SCANNING:
            raise ScannerSafetyError("Live network scanning is disabled in server policy. Enable via ENABLE_LIVE_SCANNING=True or use Nmap XML import / Demo Mode.")

        if not cls.is_nmap_available():
            raise ScannerSafetyError("Nmap executable was not found on the server PATH. Please install Nmap or use Nmap XML import / Demo Mode.")

        cls.validate_target(target)

        # Build strictly hardcoded argument lists - NEVER allow user-supplied CLI flags
        # Use -oX - to output XML directly to stdout
        if scan_type == "quick":
            nmap_args = [settings.NMAP_PATH, "-sT", "-T4", "-F", "-oX", "-", target]
        elif scan_type == "detailed":
            nmap_args = [settings.NMAP_PATH, "-sT", "-sV", "-T3", "--top-ports", "100", "-oX", "-", target]
        else:  # standard
            nmap_args = [settings.NMAP_PATH, "-sT", "-sV", "-T4", "--top-ports", "50", "-oX", "-", target]

        # Audit event
        db.add(AuditEvent(
            action="SCAN_INITIATED",
            target_type="network_target",
            target_id=target,
            details=f"Scan type: {scan_type}, Operator: {operator_username}, Flags: {' '.join(nmap_args)}",
            ip_address=operator_ip
        ))
        db.commit()

        # Assessment record
        assessment = Assessment(
            title=f"Authorized Nmap Scan - {target}",
            description=f"Live discovery scan against authorized scope {target} using preset '{scan_type}' profile.",
            assessment_type="live_nmap",
            target_scope=target,
            status="running"
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)

        start_time = time.time()
        try:
            # Subprocess without shell interpolation
            result = subprocess.run(
                nmap_args,
                capture_output=True,
                text=True,
                timeout=settings.SCAN_TIMEOUT_SECONDS,
                check=False
            )
            duration = round(time.time() - start_time, 2)

            if result.returncode != 0:
                assessment.status = "failed"
                assessment.error_log = f"Nmap exited with code {result.returncode}: {result.stderr[:1000]}"
                assessment.execution_duration_seconds = duration
                db.commit()
                return assessment

            # Parse XML output
            hosts = NmapXMLParser.parse_xml(result.stdout)
            total_assets = 0
            for h in hosts:
                total_assets += 1
                asset = Asset(
                    hostname=h["hostname"],
                    ip_address=h["ip_address"],
                    mac_address=h.get("mac_address"),
                    os_name=h.get("os_name"),
                    os_version=h.get("os_version"),
                    asset_type=h.get("asset_type", "server"),
                    criticality="MEDIUM",
                    environment="internal",
                    is_isolated=False,
                    business_impact_score=50.0
                )
                db.add(asset)
                db.flush()

                for s in h.get("services", []):
                    srv = ServicePort(
                        asset_id=asset.id,
                        port=s["port"],
                        protocol=s["protocol"],
                        service_name=s.get("service_name"),
                        product=s.get("product"),
                        version=s.get("version"),
                        banner=s.get("banner"),
                        state=s.get("state", "open")
                    )
                    db.add(srv)

            assessment.status = "completed"
            assessment.total_assets_found = total_assets
            assessment.execution_duration_seconds = duration
            db.commit()
            db.refresh(assessment)
            return assessment

        except subprocess.TimeoutExpired:
            assessment.status = "failed"
            assessment.error_log = f"Scan exceeded configured timeout of {settings.SCAN_TIMEOUT_SECONDS}s"
            assessment.execution_duration_seconds = round(time.time() - start_time, 2)
            db.commit()
            return assessment
        except Exception as e:
            assessment.status = "failed"
            assessment.error_log = str(e)
            assessment.execution_duration_seconds = round(time.time() - start_time, 2)
            db.commit()
            return assessment
