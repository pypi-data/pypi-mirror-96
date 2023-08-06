import pdb

from django.test import TestCase, tag
from edc_visit_tracking.constants import SCHEDULED

from ...constants import REQUIRED
from ...metadata import CrfMetadataGetter
from ...next_form_getter import NextFormGetter
from ..models import CrfOne, CrfThree, CrfTwo, SubjectVisit
from .metadata_test_mixin import TestMetadataMixin


class TestMetadataGetter(TestMetadataMixin, TestCase):
    def test_objects_none_no_appointment(self):
        subject_identifier = None
        visit_code = None
        getter = CrfMetadataGetter(
            subject_identifier=subject_identifier, visit_code=visit_code
        )
        self.assertEqual(getter.metadata_objects.count(), 0)

    def test_objects_not_none_without_appointment(self):
        getter = CrfMetadataGetter(
            subject_identifier=self.subject_identifier,
            visit_code=self.appointment.visit_code,
            visit_code_sequence=self.appointment.visit_code_sequence,
        )
        self.assertGreater(getter.metadata_objects.count(), 0)

    def test_objects_not_none_from_appointment(self):
        getter = CrfMetadataGetter(appointment=self.appointment)
        self.assertGreater(getter.metadata_objects.count(), 0)

    @tag("sss")
    def test_next_object(self):
        SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )
        getter = CrfMetadataGetter(appointment=self.appointment)
        visit = self.schedule.visits.get(getter.visit_code)
        # pdb.set_trace()
        objects = []
        for crf in visit.crfs:
            obj = getter.next_object(crf.show_order, entry_status=REQUIRED)
            if obj:
                objects.append(obj)
                self.assertIsNotNone(obj)
                self.assertGreater(obj.show_order, crf.show_order)
        self.assertEqual(len(objects), len(visit.crfs) - 1)

    def test_next_required_form(self):
        SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )
        getter = NextFormGetter(appointment=self.appointment, model="edc_metadata.crftwo")
        self.assertEqual(getter.next_form.model, "edc_metadata.crfthree")

    def test_next_required_form2(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )
        CrfOne.objects.create(subject_visit=subject_visit)
        crf_two = CrfTwo.objects.create(subject_visit=subject_visit)
        getter = NextFormGetter(model_obj=crf_two)
        self.assertEqual(getter.next_form.model, "edc_metadata.crfthree")

    def test_next_required_form3(self):
        subject_visit = SubjectVisit.objects.create(
            appointment=self.appointment,
            subject_identifier=self.subject_identifier,
            reason=SCHEDULED,
        )
        CrfOne.objects.create(subject_visit=subject_visit)
        CrfTwo.objects.create(subject_visit=subject_visit)
        crf_three = CrfThree.objects.create(subject_visit=subject_visit)
        getter = NextFormGetter(model_obj=crf_three)
        self.assertEqual(getter.next_form.model, "edc_metadata.crffour")

    def test_next_requisition(self):
        getter = NextFormGetter(
            appointment=self.appointment,
            model="edc_metadata.subjectrequisition",
            panel_name="one",
        )
        next_form = getter.next_form
        self.assertEqual(next_form.model, "edc_metadata.subjectrequisition")
        self.assertEqual(next_form.panel.name, "two")

    def test_next_requisition_if_last(self):
        getter = NextFormGetter(
            appointment=self.appointment,
            model="edc_metadata.subjectrequisition",
            panel_name="six",
        )
        next_form = getter.next_form
        self.assertIsNone(next_form)

    def test_next_requisition_if_not_in_visit(self):
        getter = NextFormGetter(
            appointment=self.appointment,
            model="edc_metadata.subjectrequisition",
            panel_name="blah",
        )
        next_form = getter.next_form
        self.assertIsNone(next_form)
