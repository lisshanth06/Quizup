from locust import HttpUser, task, between
import json

class QuizParticipant(HttpUser):
    """
    Simulates a participant in the CSI Quiz Platform with CSRF handling.
    """

    wait_time = between(3, 3)

    def on_start(self):
        """
        Setup: Fetch a CSRF token and attempt to find a valid Quiz ID.
        """
        # 1. Access the landing page to get a 'csrftoken' cookie
        response = self.client.get("/landing/")
        self.csrf_token = self.client.cookies.get('csrftoken', '')
        
        # 2. Try to find an active quiz ID from the API to avoid 404s
        self.quiz_id = 1  # Fallback
        with self.client.get("/landing/api/quiz-states/", name="Setup: Fetch Quiz IDs", catch_response=True) as res:
            if res.status_code == 200:
                try:
                    data = res.json()
                    if data:
                        # Use the first available quiz ID
                        self.quiz_id = list(data.keys())[0]
                except Exception:
                    pass

    @task(10)
    def poll_quiz_status(self):
        """
        Polling the status is the most common action.
        """
        self.client.get("/landing/api/quiz-states/", name="Poll Status")

    @task(3)
    def view_waiting_page(self):
        """
        URL: /quiz/<quiz_id>/waiting/
        """
        self.client.get(f"/quiz/{self.quiz_id}/waiting/", name="Waiting Page")

    @task(5)
    def view_quiz_detail(self):
        """
        URL: /quiz/<quiz_id>/
        """
        self.client.get(f"/quiz/{self.quiz_id}/", name="Quiz Question View")

    @task(2)
    def submit_answer(self):
        """
        Fixed: Includes CSRF token and valid data format for Django.
        """
        self.client.post(
            f"/quiz/{self.quiz_id}/submit/",
            data={"option": "A"},
            headers={"X-CSRFToken": self.csrf_token},
            name="Submit Answer"
        )

    @task(1)
    def report_cheat_attempt(self):
        """
        Fixed: Includes CSRF token.
        """
        self.client.post(
            f"/quiz/{self.quiz_id}/report-cheat/",
            json={"reason": "visibility_change"},
            headers={"X-CSRFToken": self.csrf_token},
            name="Report Cheat"
        )
