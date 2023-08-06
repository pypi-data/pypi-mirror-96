from django import forms
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators.form_validator import FormValidator
from edc_model.models import estimated_date_from_ago
from respond_model.form_validators import (
    CrfFormValidatorMixin,
    InitialReviewFormValidatorMixin,
)
from respond_model.utils import raise_if_clinical_review_does_not_exist

from ..constants import DRUGS
from ..models import CholInitialReview


class CholInitialReviewFormValidator(
    InitialReviewFormValidatorMixin,
    CrfFormValidatorMixin,
    FormValidator,
):
    def clean(self):
        raise_if_clinical_review_does_not_exist(self.cleaned_data.get("subject_visit"))
        self.raise_if_both_ago_and_actual_date()

        # TODO: How is CHOL managed? Like DM? Drugs and lifestyle?
        self.required_if(
            DRUGS,
            field="managed_by",
            field_required="med_start_ago",
        )

        if self.cleaned_data.get("dx_ago") and self.cleaned_data.get("med_start_ago"):
            if (
                estimated_date_from_ago(data=self.cleaned_data, ago_field="dx_ago")
                - estimated_date_from_ago(data=self.cleaned_data, ago_field="med_start_ago")
            ).days > 1:
                raise forms.ValidationError(
                    {"med_start_ago": "Invalid. Cannot be before diagnosis."}
                )


class CholInitialReviewForm(CrfModelFormMixin, forms.ModelForm):
    form_validator_cls = CholInitialReviewFormValidator

    class Meta:
        model = CholInitialReview
        fields = "__all__"
