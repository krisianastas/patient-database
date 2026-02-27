import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from homepage.models import Patient


class AuthAndPatientsApiTests(TestCase):
    def setUp(self):
        self.username = "tester"
        self.password = "safe-pass-123"
        self.user = get_user_model().objects.create_user(
            username=self.username,
            password=self.password,
        )

    def _patient_payload(self, **overrides):
        payload = {
            "emri": "John Doe",
            "nr_cel": "+355123456",
            "email": "john@example.com",
            "mjeku": "Dr. House",
            "cmimi": "100",
            "sherbimet": "Consultation",
        }
        payload.update(overrides)
        return payload

    def test_patients_requires_authentication(self):
        response = self.client.get("/api/patients/")
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {"error": "Authentication required."})

    def test_login_success_returns_session_payload(self):
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps({"username": self.username, "password": self.password}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["authenticated"])
        self.assertEqual(data["user"]["username"], self.username)

    def test_login_failure_returns_401(self):
        response = self.client.post(
            "/api/auth/login/",
            data=json.dumps({"username": self.username, "password": "wrong-pass"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(
            response.content,
            {"error": "Invalid username or password."},
        )

    def test_authenticated_user_can_crud_patients(self):
        self.client.login(username=self.username, password=self.password)

        create_response = self.client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload()),
            content_type="application/json",
        )
        self.assertEqual(create_response.status_code, 201)
        patient_id = create_response.json()["id"]

        list_response = self.client.get("/api/patients/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()["results"]), 1)

        update_response = self.client.put(
            f"/api/patients/{patient_id}/",
            data=json.dumps(self._patient_payload(emri="Jane Doe")),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()["emri"], "Jane Doe")

        delete_response = self.client.delete(f"/api/patients/{patient_id}/")
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Patient.objects.filter(pk=patient_id).exists())

    def test_logout_invalidates_session(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"status": "logged_out"})

        list_response = self.client.get("/api/patients/")
        self.assertEqual(list_response.status_code, 401)

    def test_csrf_enforced_for_mutations_with_enforced_client(self):
        csrf_client = Client(enforce_csrf_checks=True)
        csrf_client.force_login(self.user)

        without_token = csrf_client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload()),
            content_type="application/json",
        )
        self.assertEqual(without_token.status_code, 403)

        session_response = csrf_client.get("/api/auth/session/")
        self.assertEqual(session_response.status_code, 200)
        csrf_token = session_response.cookies["csrftoken"].value

        with_token = csrf_client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload(emri="Token User")),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(with_token.status_code, 201)
