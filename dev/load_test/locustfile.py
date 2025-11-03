import os

from locust import HttpUser, task, between


class HansUser(HttpUser):

    wait_time = between(0.5, 3)

    def on_start(self):
        """Login when virtual user starts."""
        credentials = {"username": os.getenv("LOAD_TEST_USER"), "password": os.getenv("LOAD_TEST_PASSWORD")}
        self.client.post("/login", json=credentials, verify=False)

    @task
    def call_video_page(self):
        """Call video view page."""
        video_uuid = os.getenv("TEST_VIDEO_UUID")
        video_sub_url = f"/video-player?uuid={video_uuid}"
        self.client.get(video_sub_url, verify=False)
