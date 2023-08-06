from django.db import models
from edc_constants.constants import NOT_APPLICABLE
from edc_model import models as edc_models
from respond_model.model_mixins import (
    InitialReviewModelMixin,
    NcdInitialReviewModelMixin,
)

from mocca_subject.model_mixins import CrfModelMixin

from ..choices import HTN_MANAGEMENT
from ..model_mixins import DiagnosisLocationModelMixin


class HtnInitialReview(
    InitialReviewModelMixin,
    DiagnosisLocationModelMixin,
    NcdInitialReviewModelMixin,
    CrfModelMixin,
    edc_models.BaseUuidModel,
):
    ncd_condition_label = "hypertension"

    managed_by = models.CharField(
        verbose_name="How is the patient's hypertension managed?",
        max_length=15,
        choices=HTN_MANAGEMENT,
        default=NOT_APPLICABLE,
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Hypertension Initial Review"
        verbose_name_plural = "Hypertension Initial Reviews"
