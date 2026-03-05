import json
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email
from django.db.models import Prefetch
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from homepage.models import Patient, PatientServiceEvent, Service


def _serialize_user(user):
    if not user:
        return None
    return {
        'id': user.id,
        'username': user.get_username(),
    }


def _serialize_service(service):
    return {
        'id': service.id,
        'name': service.name,
    }


def _serialize_service_event(event):
    return {
        'id': event.id,
        'service': _serialize_service(event.service),
        'service_date': event.service_date.isoformat() if event.service_date else None,
        'price': event.price,
        'created_at': event.created_at.isoformat() if event.created_at else None,
        'created_by': _serialize_user(event.created_by),
    }


def _serialize_patient(patient):
    events = list(patient.service_events.all())
    summary_by_id = {}
    for event in events:
        if event.service_id not in summary_by_id:
            summary_by_id[event.service_id] = _serialize_service(event.service)

    return {
        'id': patient.id,
        'emri': patient.emri,
        'nr_cel': patient.nr_cel,
        'email': patient.email,
        'mjeku': patient.mjeku,
        'service_events': [_serialize_service_event(event) for event in events],
        'service_summary': list(summary_by_id.values()),
        'created_by': _serialize_user(patient.created_by),
        'updated_by': _serialize_user(patient.updated_by),
        'data': patient.data.isoformat() if patient.data else None,
    }


def _parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return None


def _clean_optional_str(value, *, max_length=None, field_name=None, errors=None):
    if value is None:
        return None
    if not isinstance(value, str):
        if errors is not None and field_name:
            errors[field_name] = 'Must be a string.'
        return None

    cleaned = value.strip()
    if max_length and len(cleaned) > max_length:
        if errors is not None and field_name:
            errors[field_name] = f'Must be at most {max_length} characters.'
        return None
    return cleaned or None


def _validate_patient_payload(payload):
    errors = {}

    emri = _clean_optional_str(payload.get('emri'), max_length=191, field_name='emri', errors=errors)
    if not emri:
        errors['emri'] = 'Name is required.'

    nr_cel = _clean_optional_str(payload.get('nr_cel'), max_length=50, field_name='nr_cel', errors=errors)
    email = _clean_optional_str(payload.get('email'), max_length=191, field_name='email', errors=errors)
    mjeku = _clean_optional_str(payload.get('mjeku'), max_length=191, field_name='mjeku', errors=errors)

    if email:
        try:
            validate_email(email)
        except Exception:
            errors['email'] = 'Enter a valid email address.'

    if 'cmimi' in payload:
        errors['cmimi'] = 'Price belongs to services.'

    if 'service_ids' in payload:
        errors['service_ids'] = 'Use service event endpoints.'

    return {
        'cleaned_data': {
            'emri': emri,
            'nr_cel': nr_cel,
            'email': email,
            'mjeku': mjeku,
        },
        'errors': errors,
    }


def _apply_patient_fields(patient, cleaned_data, user, *, is_create=False):
    patient.emri = cleaned_data['emri']
    patient.nr_cel = cleaned_data['nr_cel']
    patient.email = cleaned_data['email']
    patient.mjeku = cleaned_data['mjeku']
    if is_create and not patient.created_by:
        patient.created_by = user
    patient.updated_by = user
    patient.save()
    return patient


def _validate_service_event_payload(payload):
    errors = {}
    service = None
    service_date = None
    price = None

    raw_service_id = payload.get('service_id')
    if not isinstance(raw_service_id, int):
        errors['service_id'] = 'Must be an integer.'
    else:
        try:
            service = Service.objects.get(pk=raw_service_id)
        except Service.DoesNotExist:
            errors['service_id'] = 'Service does not exist.'

    raw_service_date = payload.get('service_date')
    if not isinstance(raw_service_date, str):
        errors['service_date'] = 'Must be a valid date in YYYY-MM-DD format.'
    else:
        service_date = parse_date(raw_service_date.strip())
        if not service_date:
            errors['service_date'] = 'Must be a valid date in YYYY-MM-DD format.'
        elif service_date > timezone.localdate():
            errors['service_date'] = 'Service date cannot be in the future.'

    price = _clean_optional_str(payload.get('price'), max_length=50, field_name='price', errors=errors)

    return {
        'cleaned_data': {
            'service': service,
            'service_date': service_date,
            'price': price,
        },
        'errors': errors,
    }


def _parse_service_filter(raw_value):
    if not raw_value:
        return []

    values = []
    for chunk in raw_value.split(','):
        candidate = chunk.strip()
        if not candidate:
            continue
        try:
            values.append(int(candidate))
        except ValueError as exc:
            raise ValueError('service_ids must be a comma-separated list of integers.') from exc
    return list(dict.fromkeys(values))


def _patients_queryset():
    return Patient.objects.select_related('created_by', 'updated_by').prefetch_related(
        Prefetch(
            'service_events',
            queryset=PatientServiceEvent.objects.select_related('service', 'created_by').order_by('-service_date', '-id'),
        )
    )


def _auth_payload(user):
    if not user.is_authenticated:
        return {'authenticated': False, 'user': None}
    return {
        'authenticated': True,
        'user': {
            'id': user.id,
            'username': user.get_username(),
        },
    }


def json_login_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required.'}, status=401)
        return view_func(request, *args, **kwargs)

    return _wrapped


@ensure_csrf_cookie
@require_http_methods(["GET"])
def auth_session(request):
    return JsonResponse(_auth_payload(request.user))


@require_http_methods(["POST"])
def auth_login(request):
    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    username = payload.get('username')
    password = payload.get('password')
    user = authenticate(request, username=username, password=password)

    if user is None:
        return JsonResponse({'error': 'Invalid username or password.'}, status=401)

    login(request, user)
    return JsonResponse(_auth_payload(request.user))


@json_login_required
@require_http_methods(["POST"])
def auth_logout(request):
    logout(request)
    return JsonResponse({'status': 'logged_out'})


@json_login_required
@require_http_methods(["GET"])
def services_collection(request):
    services = Service.objects.order_by('name')
    return JsonResponse({'results': [_serialize_service(service) for service in services]})


@json_login_required
@require_http_methods(["GET", "POST"])
def patients_collection(request):
    if request.method == "GET":
        patients = _patients_queryset()

        try:
            service_ids = _parse_service_filter(request.GET.get('service_ids', ''))
        except ValueError as exc:
            return JsonResponse({'error': str(exc)}, status=400)

        if service_ids:
            patients = patients.filter(service_events__service_id__in=service_ids).distinct()

        data = [_serialize_patient(patient) for patient in patients.order_by('-data')]
        return JsonResponse({'results': data})

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    validation = _validate_patient_payload(payload)
    if validation['errors']:
        return JsonResponse({'errors': validation['errors']}, status=400)

    patient = _apply_patient_fields(
        Patient(),
        validation['cleaned_data'],
        request.user,
        is_create=True,
    )
    patient = _patients_queryset().get(pk=patient.pk)
    return JsonResponse(_serialize_patient(patient), status=201)


@json_login_required
@require_http_methods(["GET", "PUT", "DELETE"])
def patient_detail(request, pk):
    try:
        patient = _patients_queryset().get(pk=pk)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found.'}, status=404)

    if request.method == "GET":
        return JsonResponse(_serialize_patient(patient))

    if request.method == "DELETE":
        patient.delete()
        return JsonResponse({'status': 'deleted'})

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    validation = _validate_patient_payload(payload)
    if validation['errors']:
        return JsonResponse({'errors': validation['errors']}, status=400)

    patient = _apply_patient_fields(patient, validation['cleaned_data'], request.user)
    patient = _patients_queryset().get(pk=patient.pk)
    return JsonResponse(_serialize_patient(patient))


@json_login_required
@require_http_methods(["POST"])
def patient_service_events_collection(request, pk):
    try:
        patient = Patient.objects.get(pk=pk)
    except Patient.DoesNotExist:
        return JsonResponse({'error': 'Patient not found.'}, status=404)

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    validation = _validate_service_event_payload(payload)
    if validation['errors']:
        return JsonResponse({'errors': validation['errors']}, status=400)

    event = PatientServiceEvent.objects.create(
        patient=patient,
        service=validation['cleaned_data']['service'],
        service_date=validation['cleaned_data']['service_date'],
        price=validation['cleaned_data']['price'],
        created_by=request.user,
    )
    event = PatientServiceEvent.objects.select_related('service', 'created_by').get(pk=event.pk)
    return JsonResponse(_serialize_service_event(event), status=201)


@json_login_required
@require_http_methods(["DELETE"])
def patient_service_event_detail(request, pk, event_id):
    try:
        event = PatientServiceEvent.objects.get(pk=event_id, patient_id=pk)
    except PatientServiceEvent.DoesNotExist:
        return JsonResponse({'error': 'Service event not found.'}, status=404)

    event.delete()
    return JsonResponse({'status': 'deleted'})
