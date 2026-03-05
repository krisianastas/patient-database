import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.utils import timezone

from homepage.models import Patient, PatientServiceEvent, Service


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
        }
        payload.update(overrides)
        return payload

    def _create_service(self, name):
        return Service.objects.create(name=name)

    def _create_patient(self, **overrides):
        payload = self._patient_payload(**overrides)
        return Patient.objects.create(
            emri=payload["emri"],
            nr_cel=payload["nr_cel"],
            email=payload["email"],
            mjeku=payload["mjeku"],
            created_by=self.user,
            updated_by=self.user,
        )

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

    def test_authenticated_user_can_crud_patients_with_audit_tags(self):
        self.client.login(username=self.username, password=self.password)

        create_response = self.client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload()),
            content_type="application/json",
        )
        self.assertEqual(create_response.status_code, 201)
        created_data = create_response.json()
        patient_id = created_data["id"]
        self.assertEqual(created_data["created_by"]["username"], self.username)
        self.assertEqual(created_data["updated_by"]["username"], self.username)
        self.assertEqual(created_data["service_events"], [])
        self.assertEqual(created_data["service_summary"], [])

        self.client.logout()
        self.client.login(username="editor", password="safe-pass-456")

        update_response = self.client.put(
            f"/api/patients/{patient_id}/",
            data=json.dumps(self._patient_payload(emri="Jane Doe")),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        updated_data = update_response.json()
        self.assertEqual(updated_data["emri"], "Jane Doe")
        self.assertEqual(updated_data["created_by"]["username"], self.username)
        self.assertEqual(updated_data["updated_by"]["username"], "editor")
        self.assertEqual(updated_data["service_events"], [])
        self.assertEqual(updated_data["service_summary"], [])

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
        second = Patient.objects.create(emri="Second", created_by=self.user, updated_by=self.user)
        third = Patient.objects.create(emri="Third", created_by=self.user, updated_by=self.user)
        PatientServiceEvent.objects.create(patient=first, service=consultation, service_date=timezone.localdate(), created_by=self.user)
        PatientServiceEvent.objects.create(patient=second, service=xray, service_date=timezone.localdate(), created_by=self.user)
        PatientServiceEvent.objects.create(patient=third, service=consultation, service_date=timezone.localdate(), created_by=self.user)
        PatientServiceEvent.objects.create(patient=third, service=ultrasound, service_date=timezone.localdate(), created_by=self.user)

        response = self.client.get(f"/api/patients/?service_ids={consultation.id},{xray.id}")

        self.assertEqual(response.status_code, 200)
        names = [item["emri"] for item in response.json()["results"]]
        self.assertCountEqual(names, ["First", "Second", "Third"])

        single_response = self.client.get(f"/api/patients/?service_ids={ultrasound.id}")
        self.assertEqual(single_response.status_code, 200)
        self.assertEqual([item["emri"] for item in single_response.json()["results"]], ["Third"])

    def test_service_ids_payload_is_rejected(self):
        self.client.login(username=self.username, password=self.password)

        invalid_create = self.client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload(service_ids=[1])),
            content_type="application/json",
        )
        self.assertEqual(invalid_create.status_code, 400)
        self.assertEqual(
            invalid_create.json()["errors"]["service_ids"],
            "Use service event endpoints.",
        )

        patient = self._create_patient()
        invalid_update = self.client.put(
            f"/api/patients/{patient.id}/",
            data=json.dumps(self._patient_payload(emri="Updated", service_ids=[1])),
            content_type="application/json",
        )
        self.assertEqual(invalid_update.status_code, 400)
        self.assertEqual(
            invalid_update.json()["errors"]["service_ids"],
            "Use service event endpoints.",
        )

    def test_patient_price_payload_is_rejected(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(
            "/api/patients/",
            data=json.dumps(self._patient_payload(cmimi="100 EUR")),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["errors"]["cmimi"], "Price belongs to services.")

    def test_invalid_service_ids_filter_is_rejected(self):
        self.client.login(username=self.username, password=self.password)
        invalid_filter = self.client.get("/api/patients/?service_ids=1,two")
        self.assertEqual(invalid_filter.status_code, 400)
        self.assertEqual(
            invalid_filter.json()["error"],
            "service_ids must be a comma-separated list of integers.",
        )

    def test_create_delete_service_events_and_patient_serialization(self):
        self.client.login(username=self.username, password=self.password)
        consultation = self._create_service("Consultation")
        xray = self._create_service("X-Ray")
        patient = self._create_patient()

        first = self.client.post(
            f"/api/patients/{patient.id}/service-events/",
            data=json.dumps({"service_id": consultation.id, "service_date": "2025-01-10", "price": "100 EUR"}),
            content_type="application/json",
        )
        self.assertEqual(first.status_code, 201)

        second = self.client.post(
            f"/api/patients/{patient.id}/service-events/",
            data=json.dumps({"service_id": consultation.id, "service_date": "2025-01-10"}),
            content_type="application/json",
        )
        self.assertEqual(second.status_code, 201)

        third = self.client.post(
            f"/api/patients/{patient.id}/service-events/",
            data=json.dumps({"service_id": xray.id, "service_date": "2025-01-12"}),
            content_type="application/json",
        )
        self.assertEqual(third.status_code, 201)

        detail = self.client.get(f"/api/patients/{patient.id}/")
        self.assertEqual(detail.status_code, 200)
        detail_data = detail.json()

        event_ids = [event["id"] for event in detail_data["service_events"]]
        self.assertEqual(event_ids, [third.json()["id"], second.json()["id"], first.json()["id"]])
        self.assertEqual(
            [event["service_date"] for event in detail_data["service_events"]],
            ["2025-01-12", "2025-01-10", "2025-01-10"],
        )
        self.assertEqual(detail_data["service_events"][1]["price"], None)
        self.assertEqual(detail_data["service_events"][2]["price"], "100 EUR")
        self.assertCountEqual([item["id"] for item in detail_data["service_summary"]], [consultation.id, xray.id])

        delete_response = self.client.delete(
            f"/api/patients/{patient.id}/service-events/{second.json()['id']}/"
        )
        self.assertEqual(delete_response.status_code, 200)
        self.assertEqual(PatientServiceEvent.objects.filter(patient=patient).count(), 2)

    def test_service_event_validation(self):
        self.client.login(username=self.username, password=self.password)
        service = self._create_service("Consultation")
        patient = self._create_patient()

        invalid_service = self.client.post(
            f"/api/patients/{patient.id}/service-events/",
            data=json.dumps({"service_id": 999999, "service_date": "2025-01-10"}),
            content_type="application/json",
        )
        self.assertEqual(invalid_service.status_code, 400)
        self.assertEqual(invalid_service.json()["errors"]["service_id"], "Service does not exist.")

        invalid_date = self.client.post(
            f"/api/patients/{patient.id}/service-events/",
            data=json.dumps({"service_id": service.id, "service_date": "2025/01/10"}),
            content_type="application/json",
        )
        self.assertEqual(invalid_date.status_code, 400)
        self.assertEqual(
            invalid_date.json()["errors"]["service_date"],
            "Must be a valid date in YYYY-MM-DD format.",
        )

        future_date = (timezone.localdate() + timedelta(days=1)).isoformat()
        invalid_future = self.client.post(
            f"/api/patients/{patient.id}/service-events/",
            data=json.dumps({"service_id": service.id, "service_date": future_date}),
            content_type="application/json",
        )
        self.assertEqual(invalid_future.status_code, 400)
        self.assertEqual(
            invalid_future.json()["errors"]["service_date"],
            "Service date cannot be in the future.",
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
