from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from notes.forms import WARNING
from notes.tests.utils import (
    BaseTestCase, URL_ADD_NOTE, URL_SUCCESS_PAGE, FORM_DATA, URL_LOGIN, SLUG,
    TEXT, TITLE, URL_EDIT_NOTE, URL_DELETE_NOTE
)

User = get_user_model()


class TestNoteCreate(BaseTestCase):
    """Тесты для проверки работы маршрутов."""

    def test_dont_create_note_for_anonimus(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()
        self.assertRedirects(
            self.client.post(URL_ADD_NOTE, data=FORM_DATA),
            f'{URL_LOGIN}?next={URL_ADD_NOTE}')
        self.assertEqual(Note.objects.count(), notes_count_before)

    def test_create_note_for_auth_user(self):
        """Аутентифицированный пользователь может создать заметку."""
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        self.assertRedirects(
            self.auth_client.post(URL_ADD_NOTE, data=FORM_DATA),
            URL_SUCCESS_PAGE)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        self.assertEqual(Note.objects.last().title, TITLE)
        self.assertEqual(Note.objects.last().text, TEXT)
        self.assertEqual(Note.objects.last().slug, SLUG)
        self.assertEqual(Note.objects.last().author, self.user)
        
    def test_empty_slug(self):
        """Автоматическое формирование slug, если его не задал пользователь."""
        notes_count_before = Note.objects.count()
        FORM_DATA.pop('slug')
        self.assertRedirects(
            self.auth_client.post(URL_ADD_NOTE, data=FORM_DATA),
            URL_SUCCESS_PAGE)
        self.assertEqual(Note.objects.count(), notes_count_before + 1)
        expected_slug = slugify(FORM_DATA['title'])
        self.assertEqual(Note.objects.last().title, TITLE)
        self.assertEqual(Note.objects.last().text, TEXT)
        self.assertEqual(Note.objects.last().slug, expected_slug)
        self.assertEqual(Note.objects.last().author, self.user)

    def test_author_can_edit_note(self):
        """Только автор может редактировать свою заметку."""
        self.assertRedirects(
            self.auth_author.post(URL_EDIT_NOTE, data=FORM_DATA),
            URL_SUCCESS_PAGE)
        self.assertEqual(Note.objects.get().title, FORM_DATA['title'])
        self.assertEqual(Note.objects.get().text, FORM_DATA['text'])
        self.assertEqual(Note.objects.get().slug, FORM_DATA['slug'])
        self.assertEqual(Note.objects.get().author, self.author)

    def test_author_can_delete_note(self):
        """Только автор может удалить свою заметку."""
        notes_count_before = Note.objects.count()
        self.assertRedirects(self.auth_author.delete(URL_DELETE_NOTE),
                             URL_SUCCESS_PAGE)
        self.assertEqual(Note.objects.count(), notes_count_before - 1)

    def test_not_author_cant_delete_note(self):
        """НЕ автор не может удалить чужую заметку."""
        notes_count_before = Note.objects.count()
        note_before = Note.objects.get()
        self.assertEqual(
            self.auth_reader.delete(URL_DELETE_NOTE).status_code,
            HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), notes_count_before)
        self.assertEqual(Note.objects.get().title, note_before.title)
        self.assertEqual(Note.objects.get().text, note_before.text)
        self.assertEqual(Note.objects.get().slug, note_before.slug)
        self.assertEqual(Note.objects.get().author, note_before.author)

    def test_not_author_cant_edit_note(self):
        """НЕ автор не может редактировать чужую заметку."""
        note_before = Note.objects.get()
        self.assertEqual(
            self.auth_reader.post(URL_EDIT_NOTE, FORM_DATA).status_code,
            HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.get().title, note_before.title)
        self.assertEqual(Note.objects.get().text, note_before.text)
        self.assertEqual(Note.objects.get().slug, note_before.slug)
        self.assertEqual(Note.objects.get().author, note_before.author)

    def test_not_identical_slug(self):
        """Нельзя создать заметки с одинаковым slug."""
        notes_count_before = Note.objects.count()
        FORM_DATA['slug'] = self.note.slug
        self.assertFormError(self.auth_author.post(URL_ADD_NOTE, FORM_DATA),
                             'form', 'slug', errors=(self.note.slug + WARNING))
        self.assertEqual(Note.objects.count(), notes_count_before)
