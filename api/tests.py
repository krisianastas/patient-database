import json

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from homepage.models import Patient, Service


class AuthAndPatientsApiTests(TestCase):
    def setUp(self):
        self.username = "tester"
        self.password = "safe-pass-123"
        self.user = get_user_model().objects.create_user(
            username=self.username,
            password=self.password,
        )
        self.other_user = get_user_model().objects.create_user(
            username="editor",
            password="safe-pass-456",
        )

    def _patient_payload(self, **overrides):
        payload = {
            "emri": "John Doe",
            "nr_cel": "+355123456",
            "email": "john@example.com",
            "mjeku": "Dr. House",
            "cmimi": "100",
            "service_ids": [],
        }
        payload.update(overrides)
        return payload

    def _create_service(self, name):
        return Service.objects.create(name=name)

    def test_patients_requires_authentication(self):
        response = self.client.get("/api/patients/")
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {"error": "Authentication required."})

    def test_services_requires_authentication(self):
        response = self.client.get("/api/services/")
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

    def test_authenticated_user_can_fetch_services(self):
        self.client.login(username=self.username, password=self.password)
        self._create_service("X-Ray")
        self._create_service("Consultation")

        response = self.client.get("/api/services/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["results"],
            [
                {"id": Service.objects.get(name="Consultation").id, "name": "Consultation"},
                {"id": Service.objects.get(name="X-Ray").id, "name": "X-Ray"},
            ],
        )

    def test_authenticated_user_can_crud_patients_with_services_and_audit_tags(self):
        self.client.login(username=self.username, password=self.password)
        consultation = self._create_service("Consultation")
        xray = self._create_service("X-Ray")

        create_response = self.client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload(service_ids=[xray.id, consultation.id])),
            content_type="application/json",
        )
        self.assertEqual(create_response.status_code, 201)
        created_data = create_response.json()
        patient_id = created_data["id"]
        self.assertEqual(created_data["created_by"]["username"], self.username)
        self.assertEqual(created_data["updated_by"]["username"], self.username)
        self.assertEqual(
            created_data["services"],
            [
                {"id": consultation.id, "name": "Consultation"},
                {"id": xray.id, "name": "X-Ray"},
            ],
        )

        self.client.logout()
        self.client.login(username="editor", password="safe-pass-456")

        update_response = self.client.put(
            f"/api/patients/{patient_id}/",
            data=json.dumps(self._patient_payload(emri="Jane Doe", service_ids=[consultation.id])),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        updated_data = update_response.json()
        self.assertEqual(updated_data["emri"], "Jane Doe")
        self.assertEqual(updated_data["created_by"]["username"], self.username)
        self.assertEqual(updated_data["updated_by"]["username"], "editor")
        self.assertEqual(
            updated_data["services"],
            [{"id": consultation.id, "name": "Consultation"}],
        )

        list_response = self.client.get("/api/patients/")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(len(list_response.json()["results"]), 1)

        delete_response = self.client.delete(f"/api/patients/{patient_id}/")
        self.assertEqual(delete_response.status_code, 200)
        self.assertFalse(Patient.objects.filter(pk=patient_id).exists())

    def test_patient_list_filters_by_any_selected_service(self):
        self.client.login(username=self.username, password=self.password)
        consultation = self._create_service("Consultation")
        xray = self._create_service("X-Ray")
        ultrasound = self._create_service("Ultrasound")

        first = Patient.objects.create(emri="First", created_by=self.user, updated_by=self.user)
        first.services.set([consultation])
        second = Patient.objects.create(emri="Second", created_by=self.user, updated_by=self.user)
        second.services.set([xray])
        third = Patient.objects.create(emri="Third", created_by=self.user, updated_by=self.user)
        third.services.set([consultation, ultrasound])

        response = self.client.get(f"/api/patients/?service_ids={consultation.id},{xray.id}")

        self.assertEqual(response.status_code, 200)
        names = [item["emri"] for item in response.json()["results"]]
        self.assertCountEqual(names, ["First", "Second", "Third"])

        single_response = self.client.get(f"/api/patients/?service_ids={ultrasound.id}")
        self.assertEqual(single_response.status_code, 200)
        self.assertEqual([item["emri"] for item in single_response.json()["results"]], ["Third"])

    def test_invalid_service_ids_are_rejected(self):
        self.client.login(username=self.username, password=self.password)
        service = self._create_service("Consultation")

        invalid_write = self.client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload(service_ids="not-a-list")),
            content_type="application/json",
        )
        self.assertEqual(invalid_write.status_code, 400)
        self.assertEqual(
            invalid_write.json()["errors"]["service_ids"],
            "Must be a list of integers.",
        )

        missing_service = self.client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload(service_ids=[service.id, 9999])),
            content_type="application/json",
        )
        self.assertEqual(missing_service.status_code, 400)
        self.assertEqual(
            missing_service.json()["errors"]["service_ids"],
            "One or more selected services do not exist.",
        )

        invalid_filter = self.client.get("/api/patients/?service_ids=1,two")
        self.assertEqual(invalid_filter.status_code, 400)
        self.assertEqual(
            invalid_filter.json()["error"],
            "service_ids must be a comma-separated list of integers.",
        )

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
        service = self._create_service("Consultation")

        without_token = csrf_client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload(service_ids=[service.id])),
            content_type="application/json",
        )
        self.assertEqual(without_token.status_code, 403)

        session_response = csrf_client.get("/api/auth/session/")
        self.assertEqual(session_response.status_code, 200)
        csrf_token = session_response.cookies["csrftoken"].value

        with_token = csrf_client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload(emri="Token User", service_ids=[service.id])),
            content_type="application/json",
            HTTP_X_CSRFTOKEN=csrf_token,
        )
        self.assertEqual(with_token.status_code, 201)
