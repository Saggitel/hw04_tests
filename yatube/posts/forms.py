from django.forms import ModelForm

from .models import Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group',)
        help_texts = {'text': 'Введите сообщение', 'group': 'Выберите группу'}
        labels = {'text': 'Текст сообщения', 'group': 'Группа'}
