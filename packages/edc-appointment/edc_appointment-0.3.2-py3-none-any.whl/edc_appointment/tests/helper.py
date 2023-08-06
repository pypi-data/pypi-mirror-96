from decimal import Decimal

from edc_utils import get_utcnow
from edc_visit_schedule.site_visit_schedules import site_visit_schedules

from ..creators import UnscheduledAppointmentCreator
from .models import SubjectConsent


class Helper:
    def __init__(self, subject_identifier=None, now=None):
        self.subject_identifier = subject_identifier
        self.now = now or get_utcnow()

    def consent_and_put_on_schedule(
        self,
        subject_identifier=None,
        visit_schedule_name=None,
        schedule_name=None,
    ):
        subject_identifier = subject_identifier or self.subject_identifier
        subject_consent = SubjectConsent.objects.create(
            subject_identifier=subject_identifier, consent_datetime=self.now
        )
        visit_schedule = site_visit_schedules.get_visit_schedule(
            visit_schedule_name or "visit_schedule1"
        )
        schedule = visit_schedule.schedules.get(schedule_name or "schedule1")
        schedule.put_on_schedule(
            subject_identifier=subject_consent.subject_identifier,
            onschedule_datetime=subject_consent.consent_datetime,
        )
        return subject_consent

    @staticmethod
    def add_unscheduled_appointment(appointment=None):
        creator = UnscheduledAppointmentCreator(
            subject_identifier=appointment.subject_identifier,
            visit_schedule_name=appointment.visit_schedule_name,
            schedule_name=appointment.schedule_name,
            visit_code=appointment.visit_code,
            facility=appointment.facility,
            timepoint=appointment.timepoint + Decimal("0.1"),
        )
        return creator.appointment
