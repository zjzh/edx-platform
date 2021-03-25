"""
Defines grading configuration.
"""


from django.conf import settings

from lms.djangoapps.grades.config.waffle import ASSUME_ZERO_GRADE_IF_ABSENT
from lms.djangoapps.grades.config.waffle import waffle as waffle_func


def assume_zero_if_absent(course_key):
    """
    Returns whether an absent grade should be assumed to be zero.
    """
    return (
        settings.FEATURES.get('ASSUME_ZERO_GRADE_IF_ABSENT_FOR_ALL_TESTS') or
        waffle_func().is_enabled(ASSUME_ZERO_GRADE_IF_ABSENT)
    )
