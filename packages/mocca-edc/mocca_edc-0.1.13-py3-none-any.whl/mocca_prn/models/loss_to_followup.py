from django.db import models
from edc_action_item.models.action_model_mixin import ActionModelMixin
from edc_identifier.model_mixins import (
    NonUniqueSubjectIdentifierFieldMixin,
    TrackingModelMixin,
)
from edc_ltfu.choices import LOSS_CHOICES
from edc_ltfu.constants import LOSS_TO_FOLLOWUP_ACTION
from edc_ltfu.model_mixins import LossToFollowupModelMixin
from edc_model.models.base_uuid_model import BaseUuidModel
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_visit_schedule.model_mixins import VisitScheduleFieldsModelMixin


class LossToFollowup(
    NonUniqueSubjectIdentifierFieldMixin,
    LossToFollowupModelMixin,
    VisitScheduleFieldsModelMixin,
    SiteModelMixin,
    ActionModelMixin,
    TrackingModelMixin,
    BaseUuidModel,
):

    action_name = LOSS_TO_FOLLOWUP_ACTION

    tracking_identifier_prefix = "LF"

    loss_category = models.CharField(
        verbose_name="Category of loss to follow up",
        max_length=25,
        choices=LOSS_CHOICES,
    )

    on_site = CurrentSiteManager()

    class Meta(LossToFollowupModelMixin.Meta, BaseUuidModel.Meta):
        indexes = [
            models.Index(fields=["subject_identifier", "action_identifier", "site", "id"])
        ]
