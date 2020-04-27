"""
Views to toggle Calendar Sync settings for a user on a course
"""


import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View
from opaque_keys.edx.keys import CourseKey
from rest_framework import status
from rest_framework.decorators import action

from lms.djangoapps.courseware.courses import get_course_overview_with_access
from openedx.features.calendar_sync.api import (
    SUBSCRIBE, UNSUBSCRIBE, subscribe_user_to_calendar, unsubscribe_user_to_calendar
)
from openedx.features.calendar_sync.ics import generate_ics_for_course_start
from util.views import ensure_valid_course_key

MODE_GOOGLE = 'google'
MODE_ICS = 'ics'


class CalendarSyncView(View):
    """
    View for Calendar Sync
    """
    @method_decorator(login_required)
    @method_decorator(ensure_csrf_cookie)
    @method_decorator(ensure_valid_course_key)
    def post(self, request, course_id):
        """
        Updates the request user's calendar sync subscription status

        Arguments:
            request: HTTP request
            course_id (str): string of a course key
        """
        course_key = CourseKey.from_string(course_id)
        tool_data = request.POST.get('tool_data')
        if not tool_data:
            return HttpResponse('Tool data was not provided.', status=status.HTTP_422_UNPROCESSABLE_ENTITY)

        json_acceptable_string = tool_data.replace("'", "\"")
        data = json.loads(json_acceptable_string)
        toggle_data = data.get('toggle_data')
        if toggle_data == SUBSCRIBE:
            subscribe_user_to_calendar(request.user, course_key)
        elif toggle_data == UNSUBSCRIBE:
            unsubscribe_user_to_calendar(request.user, course_key)
        else:
            return HttpResponse('Toggle data was not provided or had unknown value.',
                                status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return redirect(reverse('openedx.course_experience.course_home', args=[course_id]))

    @action(detail=True)
    @method_decorator(ensure_valid_course_key)
    def start(self, request, course_id):
        """
        Provides a learner with calendar information for a single "start of course run" event.

        It may be useful to provide a link to this endpoint in a welcome email, for example.
        Because it may be used in contexts where the user often might not be logged in, but we don't
        want to add any extra friction and this isn't secret information, we allow anonymous access.

        If the 'mode' query param is passed, it will force a particular mode. Else this endpoint
        will decide on its own.

        Supported modes:
         * google: provides a redirect to a google calendar "add event" page
         * ics: provides a download link for an ics formatted calendar file

        Arguments:
            request: HTTP request
            course_id (str): string of a course key
        """
        mode = request.query_params.get('mode', MODE_ICS)
        course_key = CourseKey.from_string(course_id)
        course_overview = get_course_overview_with_access(request.user, 'see_exists', course_key)

        if mode == MODE_GOOGLE:
            date = course_overview.start_date.strftime('%Y%m%dT%H%M%SZ')
            add_event_url = 'https://calendar.google.com/calendar/r/eventedit'
            add_event_url += '?dates={date}/{date}'.format(date=date)
            add_event_url += '&text=' + _('{course} Begins').format(course=course_overview.display_name_with_default)
            add_event_url += '&crm=AVAILABLE'
            return HttpResponseRedirect(url=add_event_url)
        elif mode == MODE_ICS:
            ics = generate_ics_for_course_start(course_overview, request)
            return HttpResponse(ics, content_type='text/calendar')
        else:
            return HttpResponseBadRequest()
