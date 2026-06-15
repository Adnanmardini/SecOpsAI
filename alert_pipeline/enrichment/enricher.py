"""
Alert Enrichment Module
Enriches security alerts with threat intelligence from:
  - VirusTotal: IP reputation and malicious detection count
  - Shodan: Open ports, geolocation, known vulnerabilities
"""

import requests
import time
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

VT_API_KEY     = os.getenv("VIRUSTOTAL_API_KEY")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")


class AlertEnricher:

    VT_BASE_URL     = "https://www.virustotal.com/api/v3"
    SHODAN_BASE_URL = "https://api.shodan.io"

    def __init__(self):
        if not VT_API_KEY:
            logger.warning("VIRUSTOTAL_API_KEY not set in .env")
        if not SHODAN_API_KEY:
            logger.warning("SHODAN_API_KEY not set in .env")

    def enrich_ip(self, ip_address: str) -> dict:
        logger.info(f"Enriching IP: {ip_address}")
        enrichment = {
            "ip":          ip_address,
            "virustotal":  self._query_virustotal(ip_address),
            "shodan":      self._query_shodan(ip_address),
            "enriched_at": time.time(),
        }
        enrichment["severity"] = self._calculate_severity(enrichment)
        logger.info(f"Enrichment complete for {ip_address}: severity={enrichment['severity']}")
        return enrichment

    def _query_virustotal(self, ip: str) -> dict:
        if not VT_API_KEY:
            return {"error": "No API key configured"}
        try:
            response = requests.get(
                f"{self.VT_BASE_URL}/ip_addresses/{ip}",
                headers={"x-apikey": VT_API_KEY},
                timeout=10
            )
            if response.status_code == 200:
                data  = response.json()
                attrs = data.get("data", {}).get("attributes", {})
                stats = attrs.get("last_analysis_stats", {})
                return {
                    "malicious":  stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "harmless":   stats.get("harmless", 0),
                    "undetected": stats.get("undetected", 0),
                    "reputation": attrs.get("reputation", 0),
                    "country":    attrs.get("country", "unknown"),
                    "as_owner":   attrs.get("as_owner", "unknown"),
                }
            elif response.status_code == 404:
                return {"error": "IP not found in VirusTotal"}
            elif response.status_code == 429:
                return {"error": "Rate limited"}
            else:
                return {"error": f"HTTP {response.status_code}"}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except Exception as e:
            return {"error": str(e)}

    def _query_shodan(self, ip: str) -> dict:
        if not SHODAN_API_KEY:
            return {"error": "No API key configured"}
        try:
            response = requests.get(
                f"{self.SHODAN_BASE_URL}/shodan/host/{ip}",
                params={"key": SHODAN_API_KEY},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                return {
                    "open_ports":  data.get("ports", []),
                    "hostnames":   data.get("hostnames", []),
                    "country":     data.get("country_name", "unknown"),
                    "org":         data.get("org", "unknown"),
                    "vulns":       list(data.get("vulns", {}).keys())[:5],
                    "tags":        data.get("tags", []),
                    "last_update": data.get("last_update", ""),
                }
            elif response.status_code == 404:
                return {"found": False, "message": "No Shodan data for this IP"}
            else:
                return {"error": f"HTTP {response.status_code}"}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out"}
        except Exception as e:
            return {"error": str(e)}

    def _calculate_severity(self, enrichment: dict) -> str:
        vt     = enrichment.get("virustotal", {})
        shodan = enrichment.get("shodan", {})
        malicious_count      = vt.get("malicious", 0)
        has_vulns            = bool(shodan.get("vulns", []))
        sensitive_ports_open = any(
            p in shodan.get("open_ports", [])
            for p in [22, 3389, 445, 1433, 3306]
        )
        if malicious_count >= 10:
            return "critical"
        elif malicious_count >= 5 or (malicious_count > 0 and has_vulns):
            return "high"
        elif malicious_count > 0 or sensitive_ports_open:
            return "medium"
        else:
            return "low"
