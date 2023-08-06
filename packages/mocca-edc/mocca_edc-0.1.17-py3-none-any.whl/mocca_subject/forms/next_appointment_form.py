from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators.form_validator import FormValidator
from respond_model.form_validators import CrfFormValidatorMixin
from respond_model.utils import raise_if_clinical_review_does_not_exist

from mocca_consent.models import SubjectConsent

from ..models import NextAppointment


class NextAppointmentValidator(CrfFormValidatorMixin, FormValidator):
    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        self.date_not_before(
            "report_datetime",
            "appt_date",
            convert_to_date=True,
        )

    @property
    def clinic_type(self):
        return SubjectConsent.objects.get(
            subject_identifier=self.subject_identifier
        ).clinic_type


class NextAppointmentForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = NextAppointmentValidator

    class Meta:
        model = NextAppointment
        fields = "__all__"
