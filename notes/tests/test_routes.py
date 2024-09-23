from http import HTTPStatus

from django.contrib.auth import get_user_model

from notes.tests.utils import (
    BaseTestCase, URL_HOMEPAGE, URL_LOGIN, URL_LOGOUT, URL_SIGNUP,
    URL_LIST_NOTES, URL_SUCCESS_PAGE, URL_ADD_NOTE, URL_NOTE_DETAIL,
    URL_DELETE_NOTE, URL_EDIT_NOTE
)

User = get_user_model()


class TestNotes(BaseTestCase):
    """Тесты для проверки маршрутов."""

    def test_pages_availability(self):
        """Проверка доступа к страницам."""
        urls = (
            (URL_HOMEPAGE, self.client, HTTPStatus.OK),
            (URL_LOGIN, self.client, HTTPStatus.OK),
            (URL_LOGOUT, self.client, HTTPStatus.OK),
            (URL_SIGNUP, self.client, HTTPStatus.OK),
            (URL_LIST_NOTES, self.auth_reader, HTTPStatus.OK),
            (URL_SUCCESS_PAGE, self.auth_reader, HTTPStatus.OK),
            (URL_ADD_NOTE, self.auth_reader, HTTPStatus.OK),
            (URL_NOTE_DETAIL, self.auth_author, HTTPStatus.OK),
            (URL_NOTE_DETAIL, self.auth_reader, HTTPStatus.NOT_FOUND),
            (URL_DELETE_NOTE, self.auth_author, HTTPStatus.OK),
            (URL_DELETE_NOTE, self.auth_reader, HTTPStatus.NOT_FOUND),
            (URL_EDIT_NOTE, self.auth_author, HTTPStatus.OK),
            (URL_EDIT_NOTE, self.auth_reader, HTTPStatus.NOT_FOUND),
        )
        for url, user, expected_status in urls:
            with self.subTest(url=url):
                self.assertEqual(user.get(url).status_code,
                                 expected_status)

    def test_redirect_login(self):
        """Переадресация на страницу логина для анонимного пользователя."""
        urls = (
            (URL_LIST_NOTES),
            (URL_SUCCESS_PAGE),
            (URL_ADD_NOTE),
            (URL_NOTE_DETAIL),
            (URL_DELETE_NOTE),
            (URL_EDIT_NOTE),
        )
        for url in urls:
            with self.subTest(url=url):
                self.assertRedirects(
                    self.client.get(url), f'{URL_LOGIN}?next={url}'
                )
