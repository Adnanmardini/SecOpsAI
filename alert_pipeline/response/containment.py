import json
from datetime import datetime
import uuid

class ContainmentEngine:
    def __init__(self):
        self.log_file = "docs/reports/containment_actions.jsonl"
    
    def block_ip(self, ip_address, reason, alert_id, triggered_by):
        """Block malicious IP address"""
        action_id = str(uuid.uuid4())
        action = {
            "action_id": action_id,
            "type": "block_ip",
            "ip_address": ip_address,
            "reason": reason,
            "alert_id": alert_id,
            "triggered_by": triggered_by,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "executed",
            "rollback_command": f"iptables -D INPUT -s {ip_address} -j DROP"
        }
        self._log_action(action)
        return action
    
    def isolate_host(self, host_ip, reason, alert_id, triggered_by):
        """Isolate compromised host"""
        action_id = str(uuid.uuid4())
        action = {
            "action_id": action_id,
            "type": "isolate_host",
            "host_ip": host_ip,
            "reason": reason,
            "alert_id": alert_id,
            "triggered_by": triggered_by,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "executed",
            "rollback_command": f"reconnect_host {host_ip}"
        }
        self._log_action(action)
        return action
    
    def disable_user(self, username, reason, alert_id, triggered_by):
        """Disable compromised user account"""
        action_id = str(uuid.uuid4())
        action = {
            "action_id": action_id,
            "type": "disable_user",
            "username": username,
            "reason": reason,
            "alert_id": alert_id,
            "triggered_by": triggered_by,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "executed",
            "rollback_command": f"usermod -U {username}"
        }
        self._log_action(action)
        return action
    
    def _log_action(self, action):
        """Log action to file"""
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(action) + '\n')
