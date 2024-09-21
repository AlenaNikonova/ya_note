"""Строка документации блока."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

from notes.forms import NoteForm

User = get_user_model()


class TestContent(TestCase):
    """Тесты для проверки работы маршрутов."""

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

    def test_add_note_in_note_list(self):
        """Проверка наличия заметки в списке заметок после её создания."""
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_note_not_in_list_for_another_user(self):
        """Заметка не должна попадать в список заметок НЕ автора."""
        url = reverse('notes:list')
        self.client.force_login(self.reader)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_has_form(self):
        """Проверка наличия формы на страницах создания и редактирования."""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
