from django import forms
from edc_consent.form_validators import SubjectConsentFormValidatorMixin
from edc_consent.modelform_mixins import ConsentModelFormMixin
from edc_form_validators import FormValidator, FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from ..models import SubjectConsent


class SubjectConsentFormValidator(SubjectConsentFormValidatorMixin, FormValidator):
    subject_screening_model = "mocca_screening.subjectscreening"

    def clean(self):
        return super().clean()


class SubjectConsentForm(
    SiteModelFormMixin, FormValidatorMixin, ConsentModelFormMixin, forms.ModelForm
):
    form_validator_cls = SubjectConsentFormValidator

    screening_identifier = forms.CharField(
        label="Screening identifier",
        widget=forms.TextInput(attrs={"readonly": "readonly"}),
    )

    def clean_gender_of_consent(self):
        """Skip. Validated on form"""
        return None

    def clean_guardian_and_dob(self):
        """Skip. Minors not included in this trial"""
        return None

    class Meta:
        model = SubjectConsent
        fields = [
            "assessment_score",
            "confirm_identity",
            "consent_copy",
            "consent_datetime",
            "consent_reviewed",
            "consent_signature",
            "dob",
            "first_name",
            "gender",
            "identity",
            "identity_type",
            "initials",
            "is_dob_estimated",
            "is_incarcerated",
            "is_literate",
            "language",
            "last_name",
            "screening_identifier",
            "study_questions",
            "witness_name",
            "user_created",  # added for tests
        ]
        help_texts = {
            "identity": (
                "Use Country ID Number, Passport number, driver's license "
                "number, Mobile, etc"
            ),
            "witness_name": (
                "Required only if participant is illiterate. "
                "Format is 'LASTNAME, FIRSTNAME'. "
                "All uppercase separated by a comma."
            ),
        }
