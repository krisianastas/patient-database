import json
from functools import wraps

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from homepage.forms import PatientForm
from homepage.models import Patient


def _serialize_patient(patient):
    return {
        'id': patient.id,
        'emri': patient.emri,
        'nr_cel': patient.nr_cel,
        'email': patient.email,
        'mjeku': patient.mjeku,
        'cmimi': patient.cmimi,
        'sherbimet': patient.sherbimet,
        'data': patient.data.isoformat() if patient.data else None,
    }


def _parse_json_body(request):
    if not request.body:
        return {}
    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return None


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
@require_http_methods(["GET", "POST"])
def patients_collection(request):
    if request.method == "GET":
        patients = Patient.objects.all().order_by('-data')
        data = [_serialize_patient(patient) for patient in patients]
        return JsonResponse({'results': data})

    payload = _parse_json_body(request)
    if payload is None:
        return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    form = PatientForm(payload)
    if form.is_valid():
        patient = form.save()
        return JsonResponse(_serialize_patient(patient), status=201)

    return JsonResponse({'errors': form.errors}, status=400)


@json_login_required
@require_http_methods(["GET", "PUT", "DELETE"])
def patient_detail(request, pk):
    try:
        patient = Patient.objects.get(pk=pk)
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

    form = PatientForm(payload, instance=patient)
    if form.is_valid():
        patient = form.save()
        return JsonResponse(_serialize_patient(patient))

    return JsonResponse({'errors': form.errors}, status=400)
