from locust import HttpUser, task, between
import json


class DetectionAPIUser(HttpUser):
    wait_time = between(0.1, 0.5)
    token = None

    def on_start(self):
        """Get auth token when user starts."""
        response = self.client.post(
            "/auth/token",
            json={
                "username": "analyst",
                "password": "SecOpsAI@Demo2024!"
            }
        )

        if response.status_code == 200:
            self.token = response.json().get("access_token")

    @task
    def detect(self):
        """Call the detection endpoint."""
        if self.token:
            self.client.post(
                "/detect",
                json={
                    "features": [0.1] * 27
                },
                headers={
                    "Authorization": f"Bearer {self.token}"
                }
            )
