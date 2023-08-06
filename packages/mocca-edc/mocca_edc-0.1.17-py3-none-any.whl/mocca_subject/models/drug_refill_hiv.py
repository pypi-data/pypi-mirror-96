from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from edc_model import models as edc_models
from respond_model.model_mixins import DrugRefillModelMixin

from mocca_lists.models import ArvRegimens

from ..model_mixins import CrfModelMixin


class DrugRefillHiv(DrugRefillModelMixin, CrfModelMixin, edc_models.BaseUuidModel):

    rx = models.ForeignKey(
        ArvRegimens,
        verbose_name="Which medicine did the patient receive today?",
        on_delete=models.PROTECT,
    )

    class Meta(CrfModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Drug Refill: HIV"
        verbose_name_plural = "Drug Refills: HIV"
