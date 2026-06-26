import csv
import os

stats_file = "docs/reports/latency_benchmark_day5_stats.csv"

if not os.path.exists(stats_file):
    print("ERROR: Locust stats file not found")
    exit(1)

with open(stats_file, newline="") as f:
    reader = csv.DictReader(f)

    for row in reader:
        name = row.get("Name", "")

        # Skip the aggregated summary row
        if name == "Aggregated":
            continue

        try:
            p50 = float(row.get("50%", 0))
            p99 = float(row.get("99%", 999))
            rps = float(row.get("Requests/s", 0))
        except ValueError:
            continue

        print(f"\nEndpoint: {name}")
        print(f"  p50 latency: {p50:.0f} ms")
        print(f"  p99 latency: {p99:.0f} ms")
        print(f"  Requests/s : {rps:.1f}")

        if p99 < 200:
            print("  SLA (<200 ms): PASS ✅")
        else:
            print("  SLA (<200 ms): FAIL ❌")
            print("  ACTION: Optimize the endpoint or notify the API/ML team.")
