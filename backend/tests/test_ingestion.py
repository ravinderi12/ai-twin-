import pytest
from backend.app.ingestion.nmap_parser import NmapXMLParser, NmapParserError

def test_parse_valid_nmap_xml():
    with open("sample_data/sample_nmap_scan.xml", "r") as f:
        xml_content = f.read()

    hosts = NmapXMLParser.parse_xml(xml_content)
    assert len(hosts) == 2
    assert hosts[0]["ip_address"] == "192.168.10.15"
    assert hosts[0]["hostname"] == "web-frontend-01.lab.local"
    assert len(hosts[0]["services"]) == 2
    assert hosts[0]["services"][0]["port"] == 80
    assert hosts[0]["services"][0]["product"] == "Apache httpd"
    assert len(hosts[0]["services"][0]["script_findings"]) == 1
    assert hosts[0]["services"][0]["script_findings"][0]["cve_id"] == "CVE-2021-41773"

def test_reject_malformed_xml():
    malformed = "<nmaprun><host><address addr='192.168.1.1'/><ports><unclosed></host></nmaprun>"
    with pytest.raises(NmapParserError) as exc_info:
        NmapXMLParser.parse_xml(malformed)
    assert "Malformed XML" in str(exc_info.value)

def test_reject_xxe_payload():
    with open("sample_data/malicious_scan_entity_test.xml", "r") as f:
        xxe_content = f.read()

    with pytest.raises(NmapParserError) as exc_info:
        NmapXMLParser.parse_xml(xxe_content)
    assert "XXE Protection" in str(exc_info.value) or "disallowed" in str(exc_info.value)
