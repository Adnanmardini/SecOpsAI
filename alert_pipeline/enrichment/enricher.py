import requests
import time
import os
from loguru import logger
from dotenv import load_dotenv

load_dotenv()

VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")
SHODAN_API_KEY = os.getenv("SHODAN_API_KEY")
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", "0.7"))  # Fire alert if threat score > 0.7


class AlertEnricher:
    """Enriches security alerts with external threat intelligence."""

    def __init__(self):
        # ✅ V1: Safe header check — avoids sending None as API key
        self.vt_headers = {"x-apikey": VT_API_KEY} if VT_API_KEY else {}
        self.vt_base = "https://www.virustotal.com/api/v3"
        self.shodan_base = "https://api.shodan.io"

        # ✅ V1: In-memory cache to avoid repeat API calls (10-min TTL)
        self._cache = {}

    def enrich_ip(self, ip_address: str) -> dict:
        """
        Full enrichment for a source IP.
        Returns combined VirusTotal + Shodan data with calculated severity.
        Uses cache to avoid redundant API calls within 10 minutes.
        """
        # ✅ V1: Check cache before calling APIs
        if ip_address in self._cache:
            cached_time = self._cache[ip_address].get("_cached_at", 0)
            if time.time() - cached_time < 600:  # 10-minute TTL
                logger.debug(f"Returning cached enrichment for {ip_address}")
                return self._cache[ip_address]

        enrichment = {
            "ip": ip_address,
            "virustotal": self._query_virustotal_ip(ip_address),
            "shodan": self._query_shodan_ip(ip_address),
            # ✅ V2: Human-readable timestamp instead of raw _cached_at
            "enrichment_timestamp": time.time(),
            "_cached_at": time.time(),
        }

        enrichment["severity"] = self._calculate_severity(enrichment)

        # Store in cache
        self._cache[ip_address] = enrichment
        return enrichment

    def _query_virustotal_ip(self, ip: str) -> dict:
        """Query VirusTotal for IP reputation data."""
        if not VT_API_KEY:
            logger.warning("VIRUSTOTAL_API_KEY not set — skipping VT enrichment")
            return {"error": "No API key configured"}

        try:
            response = requests.get(
                f"{self.vt_base}/ip_addresses/{ip}",
                headers=self.vt_headers,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                attrs = data.get("data", {}).get("attributes", {})
                stats = attrs.get("last_analysis_stats", {})

                return {
                    "malicious":   stats.get("malicious", 0),
                    "suspicious":  stats.get("suspicious", 0),
                    "harmless":    stats.get("harmless", 0),
                    # ✅ V2: Added undetected field
                    "undetected":  stats.get("undetected", 0),
                    "reputation":  attrs.get("reputation", 0),
                    "country":     attrs.get("country", "unknown"),
                    "as_owner":    attrs.get("as_owner", "unknown"),
                }
            elif response.status_code == 404:
                return {"found": False}
            elif response.status_code == 429:
                logger.warning("VirusTotal rate limit hit — implement backoff")
                return {"error": "rate_limited"}
            else:
                return {"error": f"HTTP {response.status_code}"}

        except requests.exceptions.Timeout:
            return {"error": "timeout"}
        except Exception as e:
            logger.error(f"VirusTotal query failed: {e}")
            return {"error": str(e)}

    def _query_shodan_ip(self, ip: str) -> dict:
        """Query Shodan for host intelligence."""
        if not SHODAN_API_KEY:
            logger.warning("SHODAN_API_KEY not set — skipping Shodan enrichment")
            return {"error": "No API key configured"}

        try:
            # ✅ V1: Rate limiting for Shodan free tier (1 request/second)
            time.sleep(1)

            response = requests.get(
                f"{self.shodan_base}/shodan/host/{ip}",
                params={"key": SHODAN_API_KEY},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "open_ports": data.get("ports", []),
                    "hostnames":  data.get("hostnames", []),
                    "country":    data.get("country_name", "unknown"),
                    "org":        data.get("org", "unknown"),
                    "vulns":      list(data.get("vulns", {}).keys())[:5],  # Top 5 CVEs
                    # ✅ V2: Added tags field
                    "tags":       data.get("tags", []),
                    "last_update": data.get("last_update", ""),
                }
            elif response.status_code == 404:
                return {"found": False, "message": "No Shodan data for this IP"}
            else:
                return {"error": f"HTTP {response.status_code}"}

        except Exception as e:
            logger.error(f"Shodan query failed: {e}")
            return {"error": str(e)}

    def _calculate_severity(self, enrichment: dict) -> str:
        """
        Determine alert severity from enrichment data.
        Scale: critical > high > medium > low
        """
        vt = enrichment.get("virustotal", {})
        shodan = enrichment.get("shodan", {})

        malicious = vt.get("malicious", 0)
        has_vulns = bool(shodan.get("vulns", []))
        sensitive_ports = any(
            p in shodan.get("open_ports", [])
            for p in [22, 3389, 445, 1433, 3306]
        )

        if malicious >= 10:
            return "critical"
        elif malicious >= 5 or (malicious > 0 and has_vulns):
            return "high"
        elif malicious > 0 or sensitive_ports:
            return "medium"
        else:
            return "low”
