# -*- coding: utf-8 -*-
"""
Instructor (2) dashboard page.
"""


from bok_choy.page_object import PageObject
from bok_choy.promise import EmptyPromise, Promise

from common.test.acceptance.pages.lms.course_page import CoursePage


class InstructorDashboardPage(CoursePage):
    """
    Instructor dashboard, where course staff can manage a course.
    """
    url_path = "instructor"

    def is_browser_on_page(self):
        return self.q(css='div.instructor-dashboard-wrapper-2').present

    def get_help_element(self):
        """
        Returns the general Help button in the header.
        """
        return self.q(css='.help-link').first

    def select_membership(self):
        """
        Selects the membership tab and returns the MembershipSection
        """
        self.q(css='[data-section="membership"]').first.click()
        membership_section = MembershipPage(self.browser)
        membership_section.wait_for_page()
        return membership_section

    def select_certificates(self):
        """
        Selects the certificates tab and returns the CertificatesSection
        """
        self.q(css='[data-section="certificates"]').first.click()
        certificates_section = CertificatesPage(self.browser)
        certificates_section.wait_for_page()
        return certificates_section

    def select_bulk_email(self):
        """
        Selects the email tab and returns the bulk email section
        """
        self.q(css='[data-section="send_email"]').first.click()
        email_section = BulkEmailPage(self.browser)
        email_section.wait_for_page()
        return email_section


class BulkEmailPage(PageObject):
    """
    Bulk email section of the instructor dashboard.
    This feature is controlled by an admin panel feature flag, which is turned on via database fixture for testing.
    """
    url = None

    def is_browser_on_page(self):
        return self.q(css='[data-section=send_email].active-section').present


class MembershipPage(PageObject):
    """
    Membership section of the Instructor dashboard.
    """
    url = None

    def is_browser_on_page(self):
        return self.q(css='[data-section=membership].active-section').present

    def select_auto_enroll_section(self):
        """
        Returns the MembershipPageAutoEnrollSection page object.
        """
        return MembershipPageAutoEnrollSection(self.browser)


class MembershipPageAutoEnrollSection(PageObject):
    """
    CSV Auto Enroll section of the Membership tab of the Instructor dashboard.
    """
    url = None

    auto_enroll_browse_button_selector = '.auto_enroll_csv .file-browse input.file_field#browseBtn-auto-enroll'
    auto_enroll_upload_button_selector = '.auto_enroll_csv button[name="enrollment_signup_button"]'
    batch_enrollment_selector = '.batch-enrollment'
    NOTIFICATION_ERROR = 'error'
    NOTIFICATION_WARNING = 'warning'
    NOTIFICATION_SUCCESS = 'confirmation'

    def is_browser_on_page(self):
        return self.q(css=self.auto_enroll_browse_button_selector).present

    def is_file_attachment_browse_button_visible(self):
        """
        Returns True if the Auto-Enroll Browse button is present.
        """
        return self.q(css=self.auto_enroll_browse_button_selector).is_present()

    def is_upload_button_visible(self):
        """
        Returns True if the Auto-Enroll Upload button is present.
        """
        return self.q(css=self.auto_enroll_upload_button_selector).is_present()

    def click_upload_file_button(self):
        """
        Clicks the Auto-Enroll Upload Button.
        """
        self.q(css=self.auto_enroll_upload_button_selector).click()

    def is_notification_displayed(self, section_type):
        """
        Valid inputs for section_type: MembershipPageAutoEnrollSection.NOTIFICATION_SUCCESS /
                                       MembershipPageAutoEnrollSection.NOTIFICATION_WARNING /
                                       MembershipPageAutoEnrollSection.NOTIFICATION_ERROR
        Returns True if a {section_type} notification is displayed.
        """
        notification_selector = u'.auto_enroll_csv .results .message-%s' % section_type
        self.wait_for_element_presence(notification_selector, u"%s Notification" % section_type.title())
        return self.q(css=notification_selector).is_present()

    def first_notification_message(self, section_type):
        """
        Valid inputs for section_type: MembershipPageAutoEnrollSection.NOTIFICATION_WARNING /
                                       MembershipPageAutoEnrollSection.NOTIFICATION_ERROR
        Returns the first message from the list of messages in the {section_type} section.
        """
        error_message_selector = u'.auto_enroll_csv .results .message-%s li.summary-item' % section_type
        self.wait_for_element_presence(error_message_selector, u"%s message" % section_type.title())
        return self.q(css=error_message_selector).text[0]

    def upload_correct_csv_file(self):
        """
        Selects the correct file and clicks the upload button.
        """
        self._upload_file('auto_reg_enrollment.csv')

    def upload_csv_file_with_errors_warnings(self):
        """
        Selects the file which will generate errors and warnings and clicks the upload button.
        """
        self._upload_file('auto_reg_enrollment_errors_warnings.csv')

    def upload_non_csv_file(self):
        """
        Selects an image file and clicks the upload button.
        """
        self._upload_file('image.jpg')

    def _upload_file(self, filename):
        """
        Helper method to upload a file with registration and enrollment information.
        """
        file_path = InstructorDashboardPage.get_asset_path(filename)
        self.q(css=self.auto_enroll_browse_button_selector).results[0].send_keys(file_path)
        self.click_upload_file_button()

    def fill_enrollment_batch_text_box(self, email):
        """
        Fill in the form with the provided email and submit it.
        """
        email_selector = u"{} textarea".format(self.batch_enrollment_selector)
        enrollment_button = u"{} .enrollment-button[data-action='enroll']".format(self.batch_enrollment_selector)

        # Fill the email addresses after the email selector is visible.
        self.wait_for_element_visibility(email_selector, 'Email field is visible')
        self.q(css=email_selector).fill(email)

        # Verify enrollment button is present before clicking
        EmptyPromise(
            lambda: self.q(css=enrollment_button).present, "Enrollment button"
        ).fulfill()
        self.q(css=enrollment_button).click()

    def get_notification_text(self):
        """
        Check notification div is visible and have message.
        """
        notification_selector = u'{} .request-response'.format(self.batch_enrollment_selector)
        self.wait_for_element_visibility(notification_selector, 'Notification div is visible')
        return self.q(css=u"{} h3".format(notification_selector)).text


class CertificatesPage(PageObject):
    """
    Certificates section of the Instructor dashboard.
    """
    url = None
    PAGE_SELECTOR = 'section#certificates'

    def is_browser_on_page(self):
        return self.q(css='[data-section=certificates].active-section').present
