from locust import HttpUser, task, between
import json

class QuizParticipant(HttpUser):
    """
    Simulates a participant in the CSI Quiz Platform with CSRF handling.
    """

    wait_time = between(3, 3)

    def on_start(self):
        """
        Setup: Pick a random test account, get a CSRF token from the login page, 
        and authenticate the session.
        """
        # Extract Quiz ID dynamically
        self.quiz_id = 1
        with self.client.get("/landing/api/quiz-states/", name="Fetch Quiz IDs", catch_response=True) as res:
            if res.status_code == 200:
                try:
                    data = res.json()
                    if data:
                        self.quiz_id = list(data.keys())[0]
                except Exception:
                    pass
        
        # Get baseline CSRF token
        response = self.client.get(f"/auth/login/{self.quiz_id}/", name="Fetch Login Page")
        self.csrf_token = self.client.cookies.get('csrftoken', '')
        
        # Pick one of the 200 pre-generated test accounts
        import random
        user_index = random.randint(0, 199)
        self.email = f"loaduser{user_index}@test.com"

        # Form-based login
        self.client.post(
            f"/auth/login/{self.quiz_id}/",
            data={
                "name": f"Load Tester {user_index}",
                "email": self.email,
                "csrfmiddlewaretoken": self.csrf_token
            },
            headers={"Referer": f"http://127.0.0.1:8000/auth/login/{self.quiz_id}/"},
            name="Submit Login"
        )

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
