from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


from posts.models import Group, Post, User


class PostURLTests(TestCase):
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
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exists_at_desired_location(self):
        """Страницы доступны любому пользователю."""
        url_names = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }): HTTPStatus.OK,
            reverse('posts:profile', kwargs={
                'username': self.user
            }): HTTPStatus.OK,
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.id
            }): HTTPStatus.OK,
        }
        for url, status in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status)
