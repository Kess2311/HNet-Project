from django import forms
from .models import TreatmentSession


class TransferForm(forms.ModelForm):
    """
    A form for obtaining the hospital a patient should be transferred to.
    """

    def save_by_admin(self, patient, old_session):
        treatment_session = self.save(commit=False)
        treatment_session.patient = patient
        treatment_session.previous_session = old_session
        treatment_session.save()

    class Meta:
        model = TreatmentSession
        fields = ['treating_hospital']