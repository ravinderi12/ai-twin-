import datetime
import json
import logging
from typing import Dict, Any, Optional, List
import httpx
from sqlalchemy.orm import Session
from backend.app.core.config import settings
from backend.app.models.models import CVECacheRecord

logger = logging.getLogger(__name__)

# Curated genuine offline CVE repository for fallback and offline lab demonstration
OFFLINE_CVE_CATALOG = {
    "CVE-2021-44228": {
        "title": "Apache Log4j2 JNDI Remote Code Execution (Log4Shell)",
        "description": "Apache Log4j2 2.0-beta9 through 2.15.0 (excluding 2.12.2 and 2.3.1) JNDI features used in configuration, log messages, and parameters do not protect against attacker-controlled LDAP and other JNDI related endpoints. An attacker who can control log messages or log message parameters can execute arbitrary code loaded from LDAP servers when message lookup substitution is enabled.",
        "cvss_v3_score": 10.0,
        "cvss_v3_severity": "CRITICAL",
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
        "published_date": "2021-12-10T10:15:00.000",
        "last_modified_date": "2023-11-07T03:39:00.000",
        "reference_urls": [
            "https://nvd.nist.gov/vuln/detail/CVE-2021-44228",
            "https://logging.apache.org/log4j/2.x/security.html"
        ]
    },
    "CVE-2021-41773": {
        "title": "Apache HTTP Server 2.4.49 Path Traversal and Remote Code Execution",
        "description": "A flaw was found in a change made to path normalization in Apache HTTP Server 2.4.49. An attacker could use a path traversal attack to map URLs to files outside the directories configured by Alias-like directives. If files outside of these directories are not protected by the usual default configuration 'require all denied', these requests can succeed. If CGI scripts are also enabled for these aliased paths, this could allow for remote code execution.",
        "cvss_v3_score": 7.5,
        "cvss_v3_severity": "HIGH",
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N",
        "published_date": "2021-10-05T11:15:00.000",
        "last_modified_date": "2023-11-07T03:38:00.000",
        "reference_urls": [
            "https://nvd.nist.gov/vuln/detail/CVE-2021-41773",
            "https://httpd.apache.org/security/vulnerabilities_24.html"
        ]
    },
    "CVE-2020-1472": {
        "title": "Netlogon Elevation of Privilege (Zerologon)",
        "description": "An elevation of privilege vulnerability exists when an attacker establishes a vulnerable Netlogon secure channel connection to a domain controller, using the Netlogon Remote Protocol (MS-NRPC), aka 'Netlogon Elevation of Privilege Vulnerability'.",
        "cvss_v3_score": 10.0,
        "cvss_v3_severity": "CRITICAL",
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H",
        "published_date": "2020-08-17T19:15:00.000",
        "last_modified_date": "2023-04-26T19:27:00.000",
        "reference_urls": [
            "https://nvd.nist.gov/vuln/detail/CVE-2020-1472",
            "https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2020-1472"
        ]
    },
    "CVE-2017-0144": {
        "title": "Microsoft SMBv1 Remote Code Execution (EternalBlue)",
        "description": "The SMBv1 server in Microsoft Windows Vista SP2; Windows Server 2008 SP2 and R2 SP1; Windows 7 SP1; Windows 8.1; Windows Server 2012 Gold and R2; Windows RT 8.1; and Windows 10 Gold, 1511, and 1607; and Windows Server 2016 allows remote attackers to execute arbitrary code via crafted packets, aka 'Windows SMB Remote Code Execution Vulnerability'.",
        "cvss_v3_score": 8.1,
        "cvss_v3_severity": "HIGH",
        "cvss_vector": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H",
        "published_date": "2017-03-17T00:59:00.000",
        "last_modified_date": "2023-04-26T18:45:00.000",
        "reference_urls": [
            "https://nvd.nist.gov/vuln/detail/CVE-2017-0144",
            "https://docs.microsoft.com/en-us/security-updates/securitybulletins/2017/ms17-010"
        ]
    },
    "CVE-2020-14812": {
        "title": "Oracle MySQL Server Optimizer Denial of Service / Memory Corruption",
        "description": "Vulnerability in the MySQL Server product of Oracle MySQL (component: Server: Optimizer). Supported versions that are affected are 5.7.31 and prior and 8.0.21 and prior. Easily exploitable vulnerability allows low privileged attacker with network access via multiple protocols to compromise MySQL Server.",
        "cvss_v3_score": 7.1,
        "cvss_v3_severity": "HIGH",
        "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N",
        "published_date": "2020-10-21T15:15:00.000",
        "last_modified_date": "2022-06-28T14:11:00.000",
        "reference_urls": [
            "https://nvd.nist.gov/vuln/detail/CVE-2020-14812",
            "https://www.oracle.com/security-alerts/cpuoct2020.html"
        ]
    },
    "CVE-2023-38606": {
        "title": "Apple Kernel Operation Triangulation Vulnerability",
        "description": "An issue was addressed with improved state management in iOS and macOS. An app may be able to modify sensitive kernel state.",
        "cvss_v3_score": 7.8,
        "cvss_v3_severity": "HIGH",
        "cvss_vector": "CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H",
        "published_date": "2023-07-24T21:15:00.000",
        "last_modified_date": "2023-08-02T16:04:00.000",
        "reference_urls": ["https://nvd.nist.gov/vuln/detail/CVE-2023-38606"]
    }
}

class NVDClient:
    """
    Communicates with NIST NVD API 2.0 with local SQLite database caching,
    rate-limit compliance, and offline fallback catalog.
    """

    @classmethod
    def get_cve_details(cls, cve_id: str, db: Session) -> Optional[Dict[str, Any]]:
        cve_id = cve_id.strip().upper()

        # 1. Check local DB cache
        cached = db.query(CVECacheRecord).filter(CVECacheRecord.cve_id == cve_id).first()
        if cached:
            # Check cache TTL
            age_hours = (datetime.datetime.utcnow() - cached.cached_at).total_seconds() / 3600
            if age_hours < settings.NVD_CACHE_TTL_HOURS:
                return {
                    "cve_id": cached.cve_id,
                    "title": cached.title,
                    "description": cached.description,
                    "cvss_v3_score": cached.cvss_v3_score,
                    "cvss_v3_severity": cached.cvss_v3_severity,
                    "cvss_vector": cached.cvss_vector,
                    "published_date": cached.published_date,
                    "last_modified_date": cached.last_modified_date,
                    "reference_urls": json.loads(cached.reference_urls_json) if cached.reference_urls_json else [],
                    "source": "Local SQLite Cache",
                    "cached_at": cached.cached_at.isoformat()
                }

        # 2. Try online query to NVD API 2.0
        online_data = cls._fetch_from_nvd_api(cve_id)
        if online_data:
            # Save into DB cache
            cls._save_to_cache(db, online_data)
            online_data["source"] = "Official NIST NVD API 2.0"
            return online_data

        # 3. Fallback to genuine offline catalog if online query failed or internet is unreachable
        if cve_id in OFFLINE_CVE_CATALOG:
            cat_entry = OFFLINE_CVE_CATALOG[cve_id].copy()
            cat_entry["cve_id"] = cve_id
            cat_entry["source"] = "Curated Genuine Offline Catalog"
            cat_entry["cached_at"] = datetime.datetime.utcnow().isoformat()
            cls._save_to_cache(db, cat_entry)
            return cat_entry

        return None

    @classmethod
    def _fetch_from_nvd_api(cls, cve_id: str) -> Optional[Dict[str, Any]]:
        headers = {"User-Agent": "Cyber-Digital-Twin/1.0 (Academic Research)"}
        if settings.NVD_API_KEY:
            headers["apiKey"] = settings.NVD_API_KEY

        params = {"cveId": cve_id}
        url = settings.NVD_API_BASE_URL

        try:
            with httpx.Client(timeout=8.0) as client:
                resp = client.get(url, params=params, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    vulnerabilities = data.get("vulnerabilities", [])
                    if vulnerabilities:
                        cve_item = vulnerabilities[0].get("cve", {})
                        descriptions = cve_item.get("descriptions", [])
                        desc_text = descriptions[0].get("value", "") if descriptions else ""

                        metrics = cve_item.get("metrics", {})
                        cvss_score = 0.0
                        cvss_severity = "NONE"
                        cvss_vector = ""

                        # Try CVSS v3.1 then v3.0
                        cvss31 = metrics.get("cvssMetricV31", [])
                        cvss30 = metrics.get("cvssMetricV30", [])
                        primary_cvss = cvss31 or cvss30

                        if primary_cvss:
                            cvss_data = primary_cvss[0].get("cvssData", {})
                            cvss_score = float(cvss_data.get("baseScore", 0.0))
                            cvss_severity = cvss_data.get("baseSeverity", "MEDIUM")
                            cvss_vector = cvss_data.get("vectorString", "")

                        refs = [r.get("url") for r in cve_item.get("references", []) if r.get("url")]

                        return {
                            "cve_id": cve_id,
                            "title": f"NVD Record for {cve_id}",
                            "description": desc_text,
                            "cvss_v3_score": cvss_score,
                            "cvss_v3_severity": cvss_severity,
                            "cvss_vector": cvss_vector,
                            "published_date": cve_item.get("published"),
                            "last_modified_date": cve_item.get("lastModified"),
                            "reference_urls": refs
                        }
        except Exception as e:
            logger.warning(f"Unable to query NVD API for {cve_id}: {str(e)}")

        return None

    @classmethod
    def _save_to_cache(cls, db: Session, data: Dict[str, Any]) -> None:
        cve_id = data["cve_id"]
        existing = db.query(CVECacheRecord).filter(CVECacheRecord.cve_id == cve_id).first()
        if existing:
            existing.title = data.get("title", existing.title)
            existing.description = data.get("description", existing.description)
            existing.cvss_v3_score = data.get("cvss_v3_score", existing.cvss_v3_score)
            existing.cvss_v3_severity = data.get("cvss_v3_severity", existing.cvss_v3_severity)
            existing.cvss_vector = data.get("cvss_vector", existing.cvss_vector)
            existing.published_date = data.get("published_date")
            existing.last_modified_date = data.get("last_modified_date")
            existing.reference_urls_json = json.dumps(data.get("reference_urls", []))
            existing.cached_at = datetime.datetime.utcnow()
        else:
            rec = CVECacheRecord(
                cve_id=cve_id,
                title=data.get("title"),
                description=data.get("description"),
                cvss_v3_score=data.get("cvss_v3_score", 0.0),
                cvss_v3_severity=data.get("cvss_v3_severity", "MEDIUM"),
                cvss_vector=data.get("cvss_vector"),
                published_date=data.get("published_date"),
                last_modified_date=data.get("last_modified_date"),
                reference_urls_json=json.dumps(data.get("reference_urls", [])),
                cached_at=datetime.datetime.utcnow()
            )
            db.add(rec)
        db.commit()

    @classmethod
    def search_cves(cls, query: str, db: Session) -> List[Dict[str, Any]]:
        query = query.strip()
        results = []

        # If query looks like CVE-YYYY-NNNN
        if query.upper().startswith("CVE-"):
            res = cls.get_cve_details(query.upper(), db)
            if res:
                results.append(res)
                return results

        # Search local cache
        cached_matches = db.query(CVECacheRecord).filter(
            (CVECacheRecord.cve_id.ilike(f"%{query}%")) |
            (CVECacheRecord.title.ilike(f"%{query}%")) |
            (CVECacheRecord.description.ilike(f"%{query}%"))
        ).limit(10).all()

        for c in cached_matches:
            results.append({
                "cve_id": c.cve_id,
                "title": c.title,
                "description": c.description,
                "cvss_v3_score": c.cvss_v3_score,
                "cvss_v3_severity": c.cvss_v3_severity,
                "cvss_vector": c.cvss_vector,
                "published_date": c.published_date,
                "last_modified_date": c.last_modified_date,
                "reference_urls": json.loads(c.reference_urls_json) if c.reference_urls_json else [],
                "source": "Local SQLite Cache",
                "cached_at": c.cached_at.isoformat()
            })

        # Also search offline catalog
        for cve_id, item in OFFLINE_CVE_CATALOG.items():
            if not any(r["cve_id"] == cve_id for r in results):
                if query.lower() in cve_id.lower() or query.lower() in item["title"].lower() or query.lower() in item["description"].lower():
                    copy_item = item.copy()
                    copy_item["cve_id"] = cve_id
                    copy_item["source"] = "Curated Genuine Offline Catalog"
                    results.append(copy_item)

        return results
