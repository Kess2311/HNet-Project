from datetime import datetime
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from account.models import Patient, get_account_from_user, Doctor
from hospital.models import TreatmentSession
from hnet.logger import CreateLogEntry, readLog
from hospital.forms import TransferForm


@login_required
@permission_required('hospital.add_treatmentsession')
@user_passes_test(lambda u: not u.is_superuser)
def admit_patient(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        if patient.get_current_treatment_session() is None:
            hospital = get_account_from_user(request.user).hospital
            TreatmentSession.objects.create(patient=patient, treating_hospital=hospital)
            CreateLogEntry(request.user.username, "Patient admitted.")

    return redirect('medical:view_medical_information', patient_id=patient_id)


@login_required
@permission_required('hospital.discharge_patient')
@user_passes_test(lambda u: not u.is_superuser)
def discharge_patient(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    session = patient.get_current_treatment_session()

    if session is None:
        return redirect('medical:view_medical_information', patient_id=patient_id)

    if request.method == 'POST':
        if session.diagnosis_set.count() == 0:
            session.delete()
        else:
            session.discharge_timestamp = datetime.now()
            session.save()

        CreateLogEntry(request.user.username, "Patient discharged.")
        return render(request, 'discharge/discharge_done.html', {'patient_id': patient_id})
    else:
        return render(request, 'discharge/discharge.html', {'session': session})


@login_required
@permission_required('hospital.transfer_patient_any_hospital')
@user_passes_test(lambda u: not u.is_superuser)
def transfer_patient_as_admin(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    session = patient.get_current_treatment_session()

    if session is None:
        return render(request, 'transfer/not_admitted.html', {'patient_id': patient_id})

    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            session.discharge_timestamp = datetime.now()
            form.save_by_admin(patient, session)
            CreateLogEntry(request.user.username, "Patient transferred.")
            return render(request, 'transfer/transfer_done.html', {'patient_id': patient_id})
    else:
        form = TransferForm()

    return render(request, 'transfer/admin_transfer.html', {'form': form})


@login_required
@permission_required('hospital.transfer_patient_receiving_hospital')
@user_passes_test(lambda u: not u.is_superuser)
def transfer_patient_as_doctor(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    session = patient.get_current_treatment_session()

    if session is None:
        return redirect('medical:view_medical_information', patient_id=patient_id)

    if request.method == 'POST':
        session.discharge_timestamp = datetime.now()
        session.save()
        hospital = get_account_from_user(request.user).hospital
        new_session = TreatmentSession.objects.create(patient=patient, treating_hospital=hospital)
        new_session.previous_session = session
        new_session.save()
        CreateLogEntry(request.user.username, "Patient transferred.")
        return render(request, 'transfer/transfer_done.html', {'patient_id': patient_id})

    return render(request, 'transfer/doctor_transfer.html')


def logView(request):
    log = readLog()
    return render(request, 'hospital/viewlog.html', {"log": log})
