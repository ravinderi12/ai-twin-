import re
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

class NmapParserError(Exception):
    pass

class NmapXMLParser:
    """
    Secure and robust parser for Nmap XML output.
    Protects against XXE (XML External Entity) attacks and parses host,
    port, service, and OS information.
    """
    MAX_XML_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit

    @classmethod
    def sanitize_and_validate_xml(cls, xml_content: str) -> str:
        if len(xml_content.encode("utf-8")) > cls.MAX_XML_SIZE_BYTES:
            raise NmapParserError(f"XML payload exceeds safe limit of {cls.MAX_XML_SIZE_BYTES // (1024*1024)}MB")

        # Explicitly reject XML containing ENTITY definitions or external DTD references (XXE prevention)
        if re.search(r'<!ENTITY', xml_content, re.IGNORECASE):
            raise NmapParserError("Security violation: Custom ENTITY definitions are strictly disallowed (XXE Protection)")

        if re.search(r'<!DOCTYPE\s+\w+\s+\[', xml_content, re.IGNORECASE):
            raise NmapParserError("Security violation: Inline DTD subset with custom definitions is disallowed")

        if re.search(r'<!DOCTYPE\s+\w+\s+(SYSTEM|PUBLIC)', xml_content, re.IGNORECASE):
            raise NmapParserError("Security violation: External DTD entities (SYSTEM/PUBLIC) are disallowed")

        return xml_content

    @classmethod
    def parse_xml(cls, xml_content: str) -> List[Dict[str, Any]]:
        clean_xml = cls.sanitize_and_validate_xml(xml_content)
        try:
            root = ET.fromstring(clean_xml)
        except ET.ParseError as e:
            raise NmapParserError(f"Malformed XML: {str(e)}")

        hosts_data = []

        for host_elem in root.findall("host"):
            status_elem = host_elem.find("status")
            if status_elem is not None and status_elem.get("state") != "up":
                continue  # Skip down hosts

            ipv4 = None
            mac = None
            for addr in host_elem.findall("address"):
                addr_type = addr.get("addrtype")
                if addr_type == "ipv4":
                    ipv4 = addr.get("addr")
                elif addr_type == "mac":
                    mac = addr.get("addr")

            if not ipv4:
                continue

            # Hostnames
            hostnames = []
            hostnames_elem = host_elem.find("hostnames")
            if hostnames_elem is not None:
                for hn in hostnames_elem.findall("hostname"):
                    name = hn.get("name")
                    if name:
                        hostnames.append(name)
            primary_hostname = hostnames[0] if hostnames else f"host-{ipv4.replace('.', '-')}"

            # OS detection
            os_name = "Unknown OS"
            os_version = None
            os_elem = host_elem.find("os")
            if os_elem is not None:
                osmatch = os_elem.find("osmatch")
                if osmatch is not None:
                    os_name = osmatch.get("name", "Unknown OS")
                    os_version = osmatch.get("accuracy", "")

            # Ports & Services
            services = []
            ports_elem = host_elem.find("ports")
            if ports_elem is not None:
                for port_elem in ports_elem.findall("port"):
                    port_id = int(port_elem.get("portid", 0))
                    protocol = port_elem.get("protocol", "tcp")

                    state_elem = port_elem.find("state")
                    state = state_elem.get("state", "open") if state_elem is not None else "open"

                    service_elem = port_elem.find("service")
                    service_name = service_elem.get("name", "unknown") if service_elem is not None else "unknown"
                    product = service_elem.get("product") if service_elem is not None else None
                    version = service_elem.get("version") if service_elem is not None else None
                    extrainfo = service_elem.get("extrainfo") if service_elem is not None else None

                    # Collect scripts for potential CVE or vuln references
                    script_findings = []
                    for script in port_elem.findall("script"):
                        sid = script.get("id", "")
                        output = script.get("output", "")
                        # Look for CVE pattern
                        cves = re.findall(r'CVE-\d{4}-\d{4,7}', output)
                        if cves:
                            for c in set(cves):
                                script_findings.append({
                                    "cve_id": c,
                                    "script_id": sid,
                                    "output_snippet": output[:300]
                                })

                    services.append({
                        "port": port_id,
                        "protocol": protocol,
                        "state": state,
                        "service_name": service_name,
                        "product": product,
                        "version": version,
                        "banner": extrainfo,
                        "script_findings": script_findings
                    })

            # Derive asset type heuristically
            asset_type = "server"
            if any(s["port"] in (3306, 5432, 1433, 1521, 27017) for s in services):
                asset_type = "database"
            elif any(s["port"] in (445, 3389) for s in services) and "windows" in os_name.lower():
                asset_type = "workstation" if "server" not in os_name.lower() else "server"
            elif any(s["port"] in (80, 443, 8080) for s in services):
                asset_type = "server"

            hosts_data.append({
                "ip_address": ipv4,
                "mac_address": mac,
                "hostname": primary_hostname,
                "os_name": os_name,
                "os_version": os_version,
                "asset_type": asset_type,
                "services": services
            })

        return hosts_data
