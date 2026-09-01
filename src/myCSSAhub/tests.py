from unittest.mock import MagicMock, Mock, patch

from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, SimpleTestCase

from .views import PasswordResetView


class PasswordResetViewTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def make_request(self):
        request = self.factory.post(
            '/hub/password_reset/',
            {'email': 'member@example.com'},
        )
        request.session = {}
        request._messages = FallbackStorage(request)
        return request

    @staticmethod
    def user_queryset():
        user = Mock(pk='test-user', email='member@example.com')
        queryset = MagicMock()
        queryset.exists.return_value = True
        queryset.__iter__ = Mock(return_value=iter([user]))
        return queryset

    @patch('myCSSAhub.views.logger.exception')
    @patch('myCSSAhub.views.raw_send_mail', side_effect=TypeError('bad mail configuration'))
    @patch('myCSSAhub.views.render_to_string', return_value='reset email')
    @patch('myCSSAhub.views.UserModels.User.objects.filter')
    def test_unexpected_email_error_is_logged_without_returning_500(
            self, filter_users, _render_email, _send_email, log_exception):
        filter_users.return_value = self.user_queryset()

        response = PasswordResetView.as_view()(self.make_request())

        self.assertEqual(response.status_code, 200)
        log_exception.assert_called_once()

    @patch('myCSSAhub.views.raw_send_mail', return_value=1)
    @patch('myCSSAhub.views.render_to_string', return_value='reset email')
    @patch('myCSSAhub.views.UserModels.User.objects.filter')
    def test_successful_email_redirects_to_sent_page(
            self, filter_users, _render_email, _send_email):
        filter_users.return_value = self.user_queryset()

        response = PasswordResetView.as_view()(self.make_request())

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/hub/password_reset_sent/')
