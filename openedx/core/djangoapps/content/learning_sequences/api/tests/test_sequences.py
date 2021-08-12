"""
Tests for generic sequence-featching API tests.

Use the learning_sequences outlines API to create test data.
Do not import/create/mock learning_sequences models directly.
"""
from datetime import datetime, timezone

from django.test import TestCase
from opaque_keys.edx.keys import CourseKey, UsageKey

from ...api import replace_course_outline
from ...data import CourseOutlineData, CourseVisibility, LearningSequenceData, hash_usage_key
from ..sequences import get_learning_sequence, get_learning_sequence_by_hash
from .test_data import generate_sections


class GetLearningSequenceTestCase(TestCase):
    """
    Test get_learning_sequence and get_learning_sequence_by_hash.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Set up test data, to be reusable across all tests in this class.
        """
        super().setUpTestData()
        cls.course_key = CourseKey.from_string("course-v1:Open-edX+Learn+GetSeq")
        cls.course_outline = CourseOutlineData(
            course_key=cls.course_key,
            title="Get Learning Sequences Test Course!",
            published_at=datetime(2021, 8, 12, tzinfo=timezone.utc),
            published_version="5ebece4b69cc593d82fe2021",
            entrance_exam_id=None,
            days_early_for_beta=None,
            sections=generate_sections(cls.course_key, [0, 2, 1]),
            self_paced=False,
            course_visibility=CourseVisibility.PRIVATE
        )
        replace_course_outline(cls.course_outline)
        cls.sequence_key = cls.course_outline.sections[1].sequences[1].usage_key
        cls.sequence_key_hash = hash_usage_key(cls.sequence_key)
        cls.fake_sequence_key = UsageKey.from_string(
            "block-v1:Open-edX+Learn+GetSeq+type@sequential+block@fake_sequence"
        )
        cls.fake_sequence_key_hash = hash_usage_key(cls.fake_sequence_key)

    def test_get_learning_sequence_not_found(self):
        with self.assertRaises(LearningSequenceData.DoesNotExist):
            get_learning_sequence(self.fake_sequence_key)

    def test_get_learning_sequence_by_hash_not_found(self):
        with self.assertRaises(LearningSequenceData.DoesNotExist):
            get_learning_sequence_by_hash(self.fake_sequence_key_hash)

    def test_get_learning_sequence(self):
        sequence = get_learning_sequence(self.sequence_key)
        assert isinstance(sequence, LearningSequenceData)
        assert sequence.usage_key == self.sequence_key
        assert sequence.usage_key_hash == self.sequence_key_hash

    def test_get_learning_sequence_by_hash(self):
        sequence = get_learning_sequence_by_hash(self.sequence_key_hash)
        assert isinstance(sequence, LearningSequenceData)
        assert sequence.usage_key == self.sequence_key
        assert sequence.usage_key_hash == self.sequence_key_hash
