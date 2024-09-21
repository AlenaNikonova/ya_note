"""Строка документации блока."""

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNotes(TestCase):
    """Тесты для проверки корректного отображения заметок."""

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Простой смертный')
        cls.author = User.objects.create(username='Уважаемый человек')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability(self):
        """Главная страница доступна анонимному пользователю."""
        urls = (('notes:home'),
                ('users:login'),
                ('users:logout'),
                ('users:signup'),
                )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_and_add_note_for_auth_user(self):
        """
        Доступ к страницам с заметками, к станице добавления заметки,
        успешного добавления заметки для аутентифицированного пользователя.
        """
        urls = (
            ('notes:list'),
            ('notes:success'),
            ('notes:add'),
        )
        self.client.force_login(self.reader)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_detail_edit_delete_for_author(self):
        """
        Доступ к странице заметки, её редактирования и
        удаления для автора заметки.
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )

        urls = (
            ('notes:detail'),
            ('notes:edit'),
            ('notes:delete'),
        )

        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertAlmostEqual(response.status_code, status)

    def test_redirect_login(self):
        """Переадресация на страницу логина для анонимного пользователя."""
        urls = (
            ('notes:list'),
            ('notes:success'),
            ('notes:add'),
        )

        urls_with_slug = (
            ('notes:detail'),
            ('notes:edit'),
            ('notes:delete'),
        )
        login_url = reverse('users:login')

        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

        for name in urls_with_slug:
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
