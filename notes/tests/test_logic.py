"""""Строка документации блока."""

from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()

ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')


class TestNoteCreate(TestCase):
    """Тесты для проверки работы маршрутов."""

    TITLE = 'Заголовок'
    TEXT = 'Текст заметки'
    SLUG = 'note-slug'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Просто человек')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.author = User.objects.create(username='Уважаемый человек')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.form_data = {'title': cls.TITLE,
                         'text': cls.TEXT,
                         'slug': cls.SLUG,
                         'author': cls.user
                         }

    def test_dont_create_note_for_anonimus(self):
        """Анонимный пользователь не может создать заметку."""
        self.client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_create_note_for_auth_user(self):
        """Аутентифицированный пользователь может создать заметку."""
        response = self.auth_client.post(self.url, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.TITLE)
        self.assertEqual(note.text, self.TEXT)
        self.assertEqual(note.slug, self.SLUG)
        self.assertEqual(note.author, self.user)

    def test_empty_slug(self):
        """Автоматическое формирование slug, если его не задал пользователь."""
        self.form_data.pop('slug')
        response = self.auth_client.post(ADD_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestCreateNotes(TestCase):
    """Тесты для проверки корректного отображения заметок."""

    TITLE = 'Заголовок'
    TEXT = 'Текст заметки'
    SLUG = 'note-slug'

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Простой смертный')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.author = User.objects.create(username='Уважаемый человек')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            slug=cls.SLUG,
            author=cls.author,
        )
        cls.form_data = {'title': cls.TITLE,
                         'text': cls.TEXT,
                         'slug': cls.SLUG,
                         'author': cls.author
                         }
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.add_url = reverse('notes:add')

    def test_author_can_edit_note(self):
        """Только автор может редактировать свою заметку."""
        response = self.auth_author.post(self.edit_url, self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE)
        self.assertEqual(self.note.text, self.TEXT)
        self.assertEqual(self.note.slug, self.SLUG)

    def test_author_can_delete_note(self):
        """Только автор может удалить свою заметку."""
        response = self.auth_author.delete(self.delete_url)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 0)

    def test_not_author_cant_delete_note(self):
        """НЕ автор не может удалить чужую заметку."""
        response = self.auth_reader.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_not_author_cant_edit_note(self):
        """НЕ автор не может редактировать чужую заметку."""
        response = self.auth_reader.post(self.edit_url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.TITLE)
        self.assertEqual(self.note.text, self.TEXT)
        self.assertEqual(self.note.slug, self.SLUG)

    def test_not_unique_slug(self):
        """Нельзя создать заметки с одинаковым slug."""
        self.form_data['slug'] = self.note.slug
        response = self.auth_author.post(self.add_url, self.form_data)
        self.assertFormError(response, 'form', 'slug',
                             errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), 1)
