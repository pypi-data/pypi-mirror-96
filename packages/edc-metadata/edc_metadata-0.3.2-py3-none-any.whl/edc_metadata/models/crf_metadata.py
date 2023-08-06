from django.apps import apps as django_apps
from django.db import models
from edc_model import models as edc_models
from edc_sites.models import CurrentSiteManager, SiteModelMixin

from ..managers import CrfMetadataManager
from .crf_metadata_model_mixin import CrfMetadataModelMixin


class CrfMetadata(CrfMetadataModelMixin, SiteModelMixin, edc_models.BaseUuidModel):

    on_site = CurrentSiteManager()

    objects = CrfMetadataManager()

    def __str__(self) -> str:
        return (
            f"CrfMeta {self.model} {self.visit_schedule_name}.{self.schedule_name}."
            f"{self.visit_code}.{self.visit_code_sequence}@{self.timepoint} "
            f"{self.entry_status} {self.subject_identifier}"
        )

    def natural_key(self) -> tuple:
        return (
            self.model,
            self.subject_identifier,
            self.schedule_name,
            self.visit_schedule_name,
            self.visit_code,
            self.visit_code_sequence,
        )

    # noinspection PyTypeHints
    natural_key.dependencies = ["sites.Site"]  # type: ignore

    @property
    def verbose_name(self) -> str:
        try:
            model = django_apps.get_model(self.model)
        except LookupError as e:
            return f"{e}. You need to regenerate metadata."
        return model._meta.verbose_name

    class Meta(CrfMetadataModelMixin.Meta, edc_models.BaseUuidModel.Meta):
        verbose_name = "Crf Metadata"
        verbose_name_plural = "Crf Metadata"
        unique_together = (
            (
                "subject_identifier",
                "visit_schedule_name",
                "schedule_name",
                "visit_code",
                "visit_code_sequence",
                "model",
            ),
        )
        indexes = [
            models.Index(
                fields=[
                    "subject_identifier",
                    "visit_schedule_name",
                    "schedule_name",
                    "visit_code",
                    "visit_code_sequence",
                    "timepoint",
                    "model",
                    "entry_status",
                    "show_order",
                ]
            )
        ]
