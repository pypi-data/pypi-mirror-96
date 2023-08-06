from django import forms
from edc_constants.constants import YES
from edc_crf.modelform_mixins import CrfModelFormMixin
from edc_form_validators.form_validator import FormValidator
from edc_model.models import estimated_date_from_ago
from respond_model.form_validators import CrfFormValidatorMixin
from respond_model.utils import raise_if_not_baseline

from ..models import ClinicalReviewBaseline


class ClinicalReviewBaselineFormValidator(CrfFormValidatorMixin, FormValidator):
    def clean(self):
        raise_if_not_baseline(self.cleaned_data.get("subject_visit"))
        estimated_date_from_ago(data=self.cleaned_data, ago_field="hiv_test_ago")
        self.when_tested_required(cond="hiv")

        for cond in ["htn", "dm", "chol"]:
            estimated_date_from_ago(data=self.cleaned_data, ago_field=f"{cond}_test_ago")
            self.when_tested_required(cond=cond)
            self.required_if(YES, field=f"{cond}_test", field_required=f"{cond}_dx")

    def when_tested_required(self, cond=None):
        if self.cleaned_data.get(f"{cond}_test") == YES:
            if not self.cleaned_data.get(f"{cond}_test_ago") and not self.cleaned_data.get(
                f"{cond}_test_date"
            ):
                raise forms.ValidationError(
                    f"{cond.title()}: When was the subject tested? Either provide an "
                    "estimated time 'ago' or provide the exact date. See below."
                )


class ClinicalReviewBaselineForm(CrfModelFormMixin, forms.ModelForm):

    form_validator_cls = ClinicalReviewBaselineFormValidator

    class Meta:
        model = ClinicalReviewBaseline
        fields = "__all__"
