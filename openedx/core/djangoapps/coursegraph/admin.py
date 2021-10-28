"""
Admin site bindings for coursegraph
"""
import logging

from django.contrib import admin
from django.utils.translation import gettext as _
from edx_django_utils.admin.mixins import ReadOnlyAdminMixin

from cms.djangoapps.contentstore.outlines_regenerate import CourseOutlineRegenerate

from .serializers import ModuleStoreSerializer
from .tasks import dump_to_neo4j


log = logging.getLogger(__name__)


class CourseGraphCourseDump(CourseOverview):
    """
    Proxy model for CourseOverview.

    Does *not* create/update/delete CourseOverview objects - only reads the objects.
    Uses the course IDs of the CourseOverview objects to determine which courses
    can be dumped to CourseGraph.
    """
    class Meta:
        proxy = True

    def __str__(self):
        """Represent ourselves with the course key."""
        return str(self.id)

    @classmethod
    def get_course_outline_ids(cls):
        """
        Returns all the CourseOverview object ids.
        """
        return cls.objects.values_list('id', flat=True)


def force_dump_subset_of_courses(modeladmin, request, queryset):
    """
    TODO
    """
    all_course_keys = queryset.values_list('id', flat=True)
    if not all_course_keys:
        modeladmin.message_user(f"No courses selected.")
        return
    for course_key in all_course_keys_qs:
        log.info("Queuing force-dump to CourseGraph for %s", course_key)
        dump_to_neo4j.delay(str(course_key))
    num_courses = len(all_course_keys)
    modeladmin.message_user(_("Number of course force-dumps successfully requested: {num_courses}").format(num_courses))
force_dump_subset_of_courses.short_description = _("Force-dump selected courses to CourseGraph")


def dump_all_courses_with_new_updates(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    TODO
    """
    # TODO: next line is expensive. should be wrapped within a celery task.
    ModuleStoreSerializer.create().dump_courses_to_neo4j()
    modeladmin.message_user(request, _("All courses with new updates successfully requested."))
dump_all_courses_with_new_updates.short_description = _("Dump all courses with new updates CourseGraph")


class CourseGraphCourseDumpAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    """
    Regenerates the course outline for each selected course key.
    """
    list_display = ['id']
    ordering = ['id']
    search_fields = ['id']

    actions = [force_dump_subset_of_courses, dump_all_courses_with_new_updates]


admin.site.register(CourseGraphCourseDump, CourseGraphCourseDumpAdmin)
