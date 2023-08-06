from datetime import datetime

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import ForeignKey, OneToOneField, options
from edc_crf.stubs import CrfModelStub

from edc_visit_tracking.stubs import SubjectVisitModelStub, TSubjectVisitModelStub

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ("crf_inline_parent",)


class InlineVisitMethodsModelMixin(models.Model):
    @property
    def visit_code(self: CrfModelStub):
        return self.subject_visit.visit_code

    @property
    def subject_identifier(self: CrfModelStub):
        return self.subject_visit.subject_identifier

    class Meta:
        abstract = True


class CrfInlineModelMixin(InlineVisitMethodsModelMixin, models.Model):
    """A mixin for models used as inlines in ModelAdmin."""

    def __init__(self, *args, **kwargs) -> None:
        """Try to detect the inline parent model attribute
        name or raise.
        """
        super().__init__(*args, **kwargs)
        try:
            self._meta.crf_inline_parent
        except AttributeError:
            fks = [
                field
                for field in self._meta.fields
                if isinstance(field, (OneToOneField, ForeignKey))
            ]
            if len(fks) == 1:
                self.__class__._meta.crf_inline_parent = fks[0].name
            else:
                raise ImproperlyConfigured(
                    "CrfInlineModelMixin cannot determine the "
                    "inline parent model name. Got more than one foreign key. "
                    "Try declaring \"crf_inline_parent = '<field name>'\" "
                    "explicitly in Meta."
                )

    def __str__(self) -> str:
        return str(self.parent_instance.subject_visit)

    def natural_key(self) -> tuple:
        return self.subject_visit.natural_key()

    @property
    def parent_instance(self):
        """Return the instance of the inline parent model."""
        return getattr(self, self._meta.crf_inline_parent)

    @property
    def parent_model(self) -> TSubjectVisitModelStub:
        """Return the class of the inline parent model."""
        field = getattr(self.__class__, self._meta.crf_inline_parent).field
        try:
            return field.rel.to
        except AttributeError:
            return field.remote_field.model  # django 2.0 +

    @property
    def subject_visit(self) -> SubjectVisitModelStub:
        """Return the instance of the inline parent model's visit
        model.
        """
        return getattr(self.parent_instance, self.parent_model.visit_model_attr())

    @property
    def report_datetime(self) -> datetime:
        """Return the instance of the inline parent model's
        report_datetime.
        """
        return self.subject_visit.report_datetime

    class Meta:
        crf_inline_parent: str = None
        abstract = True
