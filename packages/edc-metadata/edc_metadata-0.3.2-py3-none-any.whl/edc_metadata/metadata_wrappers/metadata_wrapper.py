import sys
from typing import Optional, Type, Union

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.management.color import color_style
from edc_crf.stubs import CrfModelStub
from edc_visit_tracking.stubs import SubjectVisitModelStub

from ..stubs import CrfMetadataModelStub, RequisitionMetadataModelStub

style = color_style()


class MetadataWrapperError(Exception):
    pass


class DeletedInvalidMetadata(Exception):
    pass


def delete_invalid_metadata_obj(
    metadata_obj: Union[CrfMetadataModelStub, RequisitionMetadataModelStub],
    visit: SubjectVisitModelStub,
    exception: Exception = None,
):
    """Deletes the metadata object and prints a
    warning.
    """
    metadata_obj.delete()
    sys.stdout.write(
        style.NOTICE(
            f"\nDeleted invalid metadata. " f"{repr(metadata_obj)}.\nGot {exception}\n"
        )
    )
    sys.stdout.flush()
    visit.save()


class MetadataWrapper:

    """A class that wraps the corresponding model instance, or not, for the
    given metadata object and sets it to itself along with other
    attributes like the visit, model class, metadata_obj, etc.
    """

    label: Optional[str] = None

    def __init__(
        self,
        visit: SubjectVisitModelStub,
        metadata_obj: Union[CrfMetadataModelStub, RequisitionMetadataModelStub],
        **kwargs
    ) -> None:
        self._model_obj = None
        self.metadata_obj = metadata_obj
        self.visit = visit

        # visit codes (and sequence) must match
        if (self.visit.visit_code != self.metadata_obj.visit_code) or (
            self.visit.visit_code_sequence != self.metadata_obj.visit_code_sequence
        ):
            raise MetadataWrapperError(
                f"Visit code mismatch. Visit is {self.visit.visit_code}."
                f"{self.visit.visit_code_sequence} but metadata object has "
                f"{self.metadata_obj.visit_code}."
                f"{self.metadata_obj.visit_code_sequence}. Got {repr(metadata_obj)}."
            )

    def __repr__(self):
        return f"{self.__class__.__name__}({self.visit}, {self.metadata_obj})"

    @property
    def options(self) -> dict:
        """Returns a dictionary of query options."""
        return {f"{self.model_cls.visit_model_attr()}": self.visit}

    @property
    def model_obj(self) -> CrfModelStub:
        if not self._model_obj:
            try:
                self._model_obj = self.model_cls.objects.get(**self.options)
            except AttributeError as e:
                if "visit_model_attr" not in str(e):
                    raise ImproperlyConfigured(f"{e} See {repr(self.model_cls)}")
                delete_invalid_metadata_obj(self.metadata_obj, visit=self.visit, exception=e)
                raise DeletedInvalidMetadata(f"{e} Try refreshing the page (1).")
            except ObjectDoesNotExist:
                self._model_obj = None
        return self._model_obj

    @model_obj.setter
    def model_obj(self, value=None):
        self._model_obj = value

    @property
    def model_cls(self) -> Type[CrfModelStub]:
        """Returns a model class or raises for the model that
        the metadata model instance represents.
        """
        try:
            model_cls = django_apps.get_model(self.metadata_obj.model)
        except LookupError as e:
            delete_invalid_metadata_obj(self.metadata_obj, visit=self.visit, exception=e)
            raise DeletedInvalidMetadata(f"{e} Try refreshing the page (2).")
        return model_cls
