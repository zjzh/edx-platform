"""
Courseware page.
"""


from bok_choy.promise import EmptyPromise

from common.test.acceptance.pages.lms.course_page import CoursePage


class CoursewarePage(CoursePage):
    """
    Course info.
    """

    url_path = "courseware/"
    xblock_component_selector = '.vert .xblock'

    # TODO: TNL-6546: Remove sidebar selectors
    section_selector = '.chapter'
    subsection_selector = '.chapter-content-container a'

    def __init__(self, browser, course_id):
        super(CoursewarePage, self).__init__(browser, course_id)
        # self.nav = CourseNavPage(browser, self)

    def is_browser_on_page(self):
        return self.q(css='.course-content').present

    def go_to_sequential_position(self, sequential_position):
        """
        Within a section/subsection navigate to the sequential position specified by `sequential_position`.

        Arguments:
            sequential_position (int): position in sequential bar
        """
        def is_at_new_position():
            """
            Returns whether the specified tab has become active. It is defensive
            against the case where the page is still being loaded.
            """
            active_tab = self._active_sequence_tab
            try:
                return active_tab and int(active_tab.attrs('data-element')[0]) == sequential_position
            except IndexError:
                return False

        sequential_position_css = u'#sequence-list #tab_{0}'.format(sequential_position - 1)
        self.q(css=sequential_position_css).first.click()
        EmptyPromise(is_at_new_position, "Position navigation fulfilled").fulfill()
