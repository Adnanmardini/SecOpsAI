#!/bin/bash
# Usage: ./process_pcap.sh <pcap_file> [output_dir]
PCAP_FILE="$1"
OUTPUT_DIR="${2:-/tmp/zeek-output}"

if [ -z "$PCAP_FILE" ]; then
    echo "Usage: $0 <pcap_file> [output_dir]"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"
echo "[*] Processing: $PCAP_FILE"

zeek -r "$PCAP_FILE" -C \
     Log::default_logdir="$OUTPUT_DIR" \
     data-pipeline/zeek-config/local.zeek

echo "[*] Zeek log files produced in: $OUTPUT_DIR"
ls -lh "$OUTPUT_DIR"/*.log 2>/dev/null
