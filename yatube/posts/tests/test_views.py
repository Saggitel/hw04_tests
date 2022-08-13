from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from posts.models import Post, Group

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.user_2 = User.objects.create_user(username='test_user_2')
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        cls.post_2 = Post.objects.create(
            author=cls.user_2,
            text='Тестовый текст 2',
            group=cls.group_2,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:profile', kwargs={
                'username': f'{self.user}'
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': f'{self.post.id}'
            }): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': f'{self.post.id}'
            }): 'posts/create_post.html',
            reverse('posts:group_list', kwargs={
                'slug': f'{self.group.slug}'
            }): 'posts/group_list.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_uses_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.context['page_obj']
        for post in posts:
            if post.author == self.user:
                post_text = post.text
                post_author = post.author
                post_group = post.group.title
                self.assertEqual(post_text, self.post.text)
                self.assertEqual(post_author, self.user)
                self.assertEqual(post_group, self.group.title)

    def test_group_posts_uses_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={
                'slug': f'{self.group.slug}'
            }))
        posts = response.context['page_obj']
        for post in posts:
            if post.author == self.user:
                post_text = post.text
                post_group_title = post.group.title
                post_group_slug = post.group.slug
                post_group_description = post.group.description
                self.assertEqual(post_text, self.post.text)
                self.assertEqual(post_group_title, self.group.title)
                self.assertEqual(post_group_slug, self.group.slug)
                self.assertEqual(
                    post_group_description, self.group.description
                )

    def test_profile_uses_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': f'{self.user}'
            }))
        posts = response.context['page_obj']
        for post in posts:
            if post.author == self.user:
                post_author = post.author
                post_title = f'Профайл пользователя {post.author}'
                self.assertEqual(post_author, self.user)
                self.assertEqual(
                    post_title, f'Профайл пользователя {self.user}'
                )

    def test_post_detail_uses_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        NUM_OF_TEXTS_SYMBOLS_IN_TITLE = 30
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={
                'post_id': f'{self.post.id}'
            }))
        posts = response.context['post_list']
        for post in posts:
            if post.author == self.user:
                post_title = post.text[:NUM_OF_TEXTS_SYMBOLS_IN_TITLE]
                self.assertEqual(
                    post_title, self.post.text[:NUM_OF_TEXTS_SYMBOLS_IN_TITLE]
                )
                self.assertEqual(post, self.post)

    def test_post_create_uses_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_uses_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={
                'post_id': f'{self.post.id}'
            })
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_pages_show_the_post_with_the_group(self):
        """На страницах index, group_list, profile отображается пост
        с указанной группой.
        """
        post_with_group = self.post
        reverse_names = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile', kwargs={'username': f'{self.user}'})
        ]
        for reverse_name in reverse_names:
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertIn(
                    post_with_group, response.context['page_obj']
                )

    def test_post_is_not_in_the_wrong_group(self):
        """Пост с указанной группой не попал в другую группу."""
        post_with_group = self.post
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={
                'slug': f'{self.group_2.slug}'}
            )
        )
        self.assertNotIn(
            post_with_group, response.context['page_obj']
        )
