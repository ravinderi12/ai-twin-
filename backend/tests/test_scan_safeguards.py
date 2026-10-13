import pytest
from backend.app.scanners.nmap_scanner import NmapScannerService, ScannerSafetyError

def test_target_validation_safeguards():
    # Valid private / loopback addresses
    NmapScannerService.validate_target("127.0.0.1")
    NmapScannerService.validate_target("192.168.1.100")
    NmapScannerService.validate_target("10.0.1.0/24")

    # Reject public Internet IP (e.g., 8.8.8.8)
    with pytest.raises(ScannerSafetyError) as exc_info:
        NmapScannerService.validate_target("8.8.8.8")
    assert "public Internet range" in str(exc_info.value)

    # Reject invalid target syntax
    with pytest.raises(ScannerSafetyError) as exc_info2:
        NmapScannerService.validate_target("invalid..ip..format")
    assert "Invalid target format" in str(exc_info2.value)
