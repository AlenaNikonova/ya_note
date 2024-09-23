from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()

URL_HOMEPAGE = reverse('notes:home')
URL_LOGIN = reverse('users:login')
URL_LOGOUT = reverse('users:logout')
URL_SIGNUP = reverse('users:signup')
URL_LIST_NOTES = reverse('notes:list')
URL_SUCCESS_PAGE = reverse('notes:success')
URL_ADD_NOTE = reverse('notes:add')
SLUG = 'note-slug'
TITLE = 'Заголовок'
TEXT = 'Текст заметки'
URL_NOTE_DETAIL = reverse('notes:detail', args=(SLUG,))
URL_DELETE_NOTE = reverse('notes:delete', args=(SLUG,))
URL_EDIT_NOTE = reverse('notes:edit', args=(SLUG,))

FORM_DATA = {'title': TITLE,
             'text': TEXT,
             'slug': SLUG,
             }


class BaseTestCase(TestCase):
    """Базовый класс для тестов."""

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.reader = User.objects.create(username='Простой смертный')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.author = User.objects.create(username='Уважаемый человек')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.user = User.objects.create(username='Просто человек')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
