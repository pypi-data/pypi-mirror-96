import arrow
from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ValidationError
from edc_model.models import datetime_not_future
from edc_protocol.validators import datetime_not_before_study_start
from edc_utils.text import convert_php_dateformat


class CrfReportDateAllowanceError(Exception):
    pass


class CrfReportDateBeforeStudyStart(Exception):
    pass


class CrfReportDateIsFuture(Exception):
    pass


class CrfDateValidator:
    report_datetime_allowance = None
    allow_report_datetime_before_visit = False

    def __init__(
        self,
        report_datetime=None,
        visit_report_datetime=None,
        report_datetime_allowance=None,
        allow_report_datetime_before_visit=None,
        created=None,
        modified=None,
        subject_identifier=None,
    ):
        self.allow_report_datetime_before_visit = (
            allow_report_datetime_before_visit or self.allow_report_datetime_before_visit
        )
        self.report_datetime_allowance = (
            report_datetime_allowance or self.report_datetime_allowance
        )
        if not self.report_datetime_allowance:
            app_config = django_apps.get_app_config("edc_visit_tracking")
            self.report_datetime_allowance = app_config.report_datetime_allowance
        self.report_datetime = (
            arrow.Arrow.fromdatetime(report_datetime, report_datetime.tzinfo)
            .to("utc")
            .datetime
        )
        self.visit_report_datetime = (
            arrow.Arrow.fromdatetime(visit_report_datetime, visit_report_datetime.tzinfo)
            .to("utc")
            .datetime
        )
        self.created = created
        self.modified = modified
        self.subject_identifier = subject_identifier
        self.validate()

    def validate(self):
        # datetime_not_before_study_start
        try:
            datetime_not_before_study_start(self.report_datetime)
        except ValidationError as e:
            message = e.message if hasattr(e, "message") else str(e)
            raise CrfReportDateBeforeStudyStart(message)
        # datetime_not_future
        try:
            datetime_not_future(self.report_datetime)
        except ValidationError as e:
            message = e.message if hasattr(e, "message") else str(e)
            raise CrfReportDateIsFuture(message)

        formatted_visit_datetime = self.visit_report_datetime.strftime(
            convert_php_dateformat(settings.SHORT_DATE_FORMAT)
        )

        # not before the visit report_datetime
        if (
            not self.allow_report_datetime_before_visit
            and self.report_datetime.date() < self.visit_report_datetime.date()
        ):
            raise CrfReportDateAllowanceError(
                "Report datetime may not be before the visit report datetime. "
                f"Visit report datetime is {formatted_visit_datetime}. "
            )

        # not more than x days greater than the visit report_datetime
        # if self.report_datetime_allowance > 0:
        max_allowed_report_datetime = self.visit_report_datetime + relativedelta(
            days=self.report_datetime_allowance
        )
        if self.report_datetime.date() > max_allowed_report_datetime.date():
            diff = (
                max_allowed_report_datetime.date() - self.visit_report_datetime.date()
            ).days
            raise CrfReportDateAllowanceError(
                f"Report datetime may not be more than {self.report_datetime_allowance} "
                f"days greater than the visit report datetime. Got {diff} days."
                f"Visit report datetime is {formatted_visit_datetime}. "
                f"See also AppConfig.report_datetime_allowance."
            )
