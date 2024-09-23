from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from notes.tests.utils import URL_LIST_NOTES, BaseTestCase

User = get_user_model()


class TestContent(BaseTestCase):
    """Тесты для проверки контента."""
    def test_note_in_list_for_author(self):
        """Проверка наличия заметки в списке заметок после её создания."""
        response = self.auth_author.get(URL_LIST_NOTES)
        self.assertIn(self.note, response.context['note_list'])

    def test_note_not_in_list_for_another_user(self):
        """Заметка не должна попадать в список заметок НЕ автора."""
        response = self.auth_reader.get(URL_LIST_NOTES)
        self.assertNotIn(self.note, response.context['note_list'])

    def test_has_form(self):
        """Проверка наличия формы на страницах создания и редактирования."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.assertIsInstance(
                    self.auth_author.get(url).context.get('form'), NoteForm)
