## Rule Set 1: C2 Beaconing Detection
MITRE ATT&CK: T1071 Application Layer Protocol
Sub-technique: T1071.001 Web Protocols

### Rule SID 1000001: Suspicious outbound high port
Logic: Connection to ports 4444, 6666, 8888, 31337, or 1337. It checks for 5 or more connections in 300 seconds.
Rationale: Hackers use these ports for control.
False positive risk: Tools like Jupyter use port 8888.
Tuning: Add safe server IPs to a whitelist.

### Rule SID 1000002: Regular small HTTP connections
Logic: Web requests with tiny response bodies under 200 bytes. It checks for 10 or more requests in 600 seconds.
Rationale: Malware sends small signals to stay alive.
False positive risk: Health check tools can look like this.

### Rule SID 1000003: HTTP with no User-Agent
Logic: Web requests that do not show a browser name.
Rationale: Real browsers always show a name. Malware often forgets this.
False positive risk: Very low.

## Rule Set 2: DNS Tunneling Detection
MITRE ATT&CK: T1071.004 Application Layer Protocol: DNS

### Rule SID 1000010: Abnormally long DNS query
Logic: DNS names longer than 150 characters.
Rationale: Hackers hide stolen data in very long names.
False positive risk: Some CDN providers use long names.

### Rule SID 1000011: High-volume DNS query rate
Logic: More than 100 DNS requests in 60 seconds from one source.
Rationale: Moving data through DNS is slow and needs many requests.
False positive risk: Internal DNS servers.
Tuning: Do not monitor internal DNS server IPs.

### Rule SID 1000012: Suspicious TXT record query
Logic: Requests for TXT records with more than 10 queries in 60 seconds.
Rationale: Hackers use TXT records because they can hold more data.
False positive risk: Very low.

## Rule Set 3: Lateral Movement Detection
MITRE ATT&CK: T1021 Remote Services

### Rule SID 1000020: SMB connections to internal host
Logic: File sharing connections with 5 or more attempts in 120 seconds.
Rationale: Hackers search for files after they get inside.
False positive risk: Normal file server use.

### Rule SID 1000021: RDP from internal workstation
Logic: Remote desktop connections from normal computers.
Rationale: Only admins should use remote desktop. Normal users should not.
False positive risk: IT staff helping users.

### Rule SID 1000022: WMI/DCOM lateral movement
Logic: Administrative commands sent at a rate of 10 per minute.
Rationale: Hackers use these to take control of other computers.
False positive risk: Software management tools.

## Rule Set 4: Data Exfiltration Detection
MITRE ATT&CK: T1041 Exfiltration Over C2 Channel

### Rule SID 1000030: Large outbound data transfer
Logic: Sending more than 1 megabyte in a single transfer.
Rationale: This identifies a hacker stealing a large file.
False positive risk: System updates or backups.

### Rule SID 1000031: Outbound FTP to external IP
Logic: Any FTP transfer to a public IP address.
Rationale: FTP is old and not secure. Hackers use it to move data easily.
False positive risk: Very low.

### Rule SID 1000032: Large HTTP POST
Logic: Sending data chunks larger than 50000 bytes more than 5 times in 300 seconds.
Rationale: This finds hackers hiding thefts in small pieces.
False positive risk: Uploading files to web apps.
