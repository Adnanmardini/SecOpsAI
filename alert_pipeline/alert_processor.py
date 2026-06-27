import time


def process_alert(alert_data):
    """
    Basic alert processing function.
    """
    return {
        "status": "processed",
        "alert": alert_data
    }


if __name__ == "__main__":
    print("Alert Pipeline started. Waiting for alerts...")

    while True:
        sample_alert = {
            "id": 1,
            "severity": "high",
            "message": "Suspicious activity detected"
        }

        result = process_alert(sample_alert)
        print(result)

        # simulate waiting for new alerts
        time.sleep(30)
