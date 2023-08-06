from django.db import models
from edc_model import models as edc_models
from respond_model.model_mixins import DrugRefillModelMixin

from mocca_lists.models import DmTreatments

from ..model_mixins import CrfModelMixin


class DrugRefillDm(DrugRefillModelMixin, CrfModelMixin, edc_models.BaseUuidModel):

    rx = models.ManyToManyField(
        DmTreatments,
        verbose_name="Which medicine did the patient receive today?",
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Drug Refill: Diabetes"
        verbose_name_plural = "Drug Refills: Diabetes"
