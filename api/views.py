import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
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


@csrf_exempt
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


@csrf_exempt
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
