from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Card
from .constants import CATEGORY_CHOICES

User = get_user_model()

class CardAPITestCase(APITestCase):
    def setUp(self):
        # Создаём двух пользователей: владельца и чужого
        self.user1 = User.objects.create_user(login='owner', password='pass123')
        self.user2 = User.objects.create_user(login='other', password='pass123')
        # Создаём карточку, принадлежащую user1
        self.card = Card.objects.create(
            title='Test Card',
            description='Description',
            budget=1000.00,
            category='Technic',
            urls=['https://example.com'],
            user=self.user1
        )
        # URL-адреса (используем reverse для динамичности)
        self.cards_list_url = reverse('card-list')  # из роутера DefaultRouter
        self.card_detail_url = reverse('card-detail', args=[self.card.id])
        self.upload_url = reverse('file-upload')  # если добавили

    def authenticate(self, user):
        # Принудительная аутентификация для тестов
        self.client.force_authenticate(user=user)

    # ------ ТЕСТЫ РЕГИСТРАЦИИ (если есть эндпоинт) ------
    def test_user_registration_success(self):
        url = reverse('user-list')  # если зарегистрирован UserViewSet
        data = {
            'login': 'newuser',
            'password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(login='newuser').exists())

    def test_user_registration_duplicate_login(self):
        url = reverse('user-list')
        data = {'login': 'owner', 'password': 'pass123'}  # уже существует
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------ ТЕСТЫ ПОЛУЧЕНИЯ ТОКЕНА (логин) ------
    def test_login_success(self):
        url = reverse('token_obtain_pair')  # ваш путь для токена
        data = {'login': 'owner', 'password': 'pass123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_password(self):
        url = reverse('token_obtain_pair')
        data = {'login': 'owner', 'password': 'wrong'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ------ ТЕСТЫ CRUD КАРТОЧЕК ------
    def test_create_card_success(self):
        self.authenticate(self.user1)
        data = {
            'title': 'New Card',
            'description': 'New desc',
            'budget': 500.00,
            'category': 'Clothes',
            'urls': ['https://test.com'],
            'image': ''
        }
        response = self.client.post(self.cards_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Card.objects.count(), 2)  # одна была в setUp
        self.assertEqual(response.data['user'], self.user1.id)
        # Проверяем, что created_at игнорируется
        self.assertNotEqual(response.data.get('created_at'), '2000-01-01T00:00:00Z')

    def test_create_card_invalid_data(self):
        self.authenticate(self.user1)
        data = {'title': '', 'budget': -100, 'category': 'Invalid'}  # невалидные
        response = self.client.post(self.cards_list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_list_cards_unauthenticated(self):
        # Без токена должен возвращать 401
        response = self.client.get(self.cards_list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_cards_authenticated(self):
        self.authenticate(self.user1)
        response = self.client.get(self.cards_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем структуру пагинации
        self.assertIn('results', response.data)
        self.assertIn('count', response.data)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_filter_by_category(self):
        self.authenticate(self.user1)
        # Создадим ещё карточку другой категории
        Card.objects.create(
            title='Another',
            budget=200,
            category='Books',
            user=self.user1
        )
        response = self.client.get(self.cards_list_url, {'category': 'Technic'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(all(card['category'] == 'Technic' for card in results))

    def test_search_by_title(self):
        self.authenticate(self.user1)
        response = self.client.get(self.cards_list_url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertTrue(any('Test' in card['title'] for card in results))

    def test_retrieve_card_owner(self):
        self.authenticate(self.user1)
        response = self.client.get(self.card_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.card.id)

    def test_retrieve_card_other(self):
        self.authenticate(self.user2)
        response = self.client.get(self.card_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)  # карточка доступна для чтения всем
        # (если разрешено) – можно проверить, что данные верны

    def test_update_card_owner(self):
        self.authenticate(self.user1)
        data = {'title': 'Updated Title', 'budget': 2000, 'category': 'Technic'}
        response = self.client.patch(self.card_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.card.refresh_from_db()
        self.assertEqual(self.card.title, 'Updated Title')
        self.assertIsNotNone(self.card.created_at)

    def test_update_card_other(self):
        self.authenticate(self.user2)
        data = {'title': 'Hacked'}
        response = self.client.patch(self.card_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # ожидаем запрет

    def test_delete_card_owner(self):
        self.authenticate(self.user1)
        response = self.client.delete(self.card_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Card.objects.filter(id=self.card.id).exists())

    def test_delete_card_other(self):
        self.authenticate(self.user2)
        response = self.client.delete(self.card_detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ------ ТЕСТЫ ЗАГРУЗКИ ФАЙЛОВ ------
    def test_upload_image_success(self):
        self.authenticate(self.user1)
        # Создаём тестовый файл
        file = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
        response = self.client.post(self.upload_url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('url', response.data)
        self.assertTrue(response.data['url'].startswith('http://testserver/media/'))

    def test_upload_non_image(self):
        self.authenticate(self.user1)
        file = SimpleUploadedFile("test.txt", b"text", content_type="text/plain")
        response = self.client.post(self.upload_url, {'file': file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_upload_large_file(self):
        self.authenticate(self.user1)
        # Создаём файл размером 6 МБ
        large_file = SimpleUploadedFile("large.jpg", b"x" * (6 * 1024 * 1024), content_type="image/jpeg")
        response = self.client.post(self.upload_url, {'file': large_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)