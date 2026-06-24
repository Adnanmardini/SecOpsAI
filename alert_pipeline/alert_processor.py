def process_alert(alert_data):
    """
    Basic alert processing function.
    """
    return {
        "status": "processed",
        "alert": alert_data
    }


if __name__ == "__main__":
    sample_alert = {
        "id": 1,
        "severity": "high",
        "message": "Suspicious activity detected"
    }

    print(process_alert(sample_alert))
