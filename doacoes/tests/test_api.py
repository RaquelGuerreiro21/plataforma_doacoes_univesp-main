from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from doacoes.models import Doador, Recebedor, Item, Doacao

User = get_user_model()

class APITestCase(TestCase):
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nome_completo='Test User'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Criar objetos para testes
        self.doador = Doador.objects.create(
            nome='João Silva',
            email='joao@email.com'
        )
        self.recebedor = Recebedor.objects.create(
            nome='Maria Santos',
            email='maria@email.com'
        )
        self.item = Item.objects.create(
            nome='Camiseta',
            tipo='RO',
            doador=self.doador
        )
        self.doacao = Doacao.objects.create(
            doador=self.doador,
            recebedor=self.recebedor,
            item=self.item
        )

    def test_list_doacoes(self):
        """Testa listagem de doações via API"""
        url = reverse('doacao-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_doacao(self):
        """Testa criação de doação via API"""
        url = reverse('doacao-list')
        data = {
            'doador': self.doador.id,
            'recebedor': self.recebedor.id,
            'item': self.item.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doacao.objects.count(), 2)

    def test_retrieve_doacao(self):
        """Testa recuperação de doação específica via API"""
        url = reverse('doacao-detail', args=[self.doacao.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['doador'], self.doador.id)

    def test_delete_doacao(self):
        """Testa exclusão de doação via API"""
        url = reverse('doacao-detail', args=[self.doacao.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Doacao.objects.count(), 0)

    def test_list_doadores(self):
        """Testa listagem de doadores via API"""
        url = reverse('doador-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_doador(self):
        """Testa criação de doador via API"""
        url = reverse('doador-list')
        data = {
            'nome': 'Pedro Santos',
            'email': 'pedro@email.com',
            'telefone': '11977777777'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Doador.objects.count(), 2)

    def test_list_recebedores(self):
        """Testa listagem de recebedores via API"""
        url = reverse('recebedor-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_recebedor(self):
        """Testa criação de recebedor via API"""
        url = reverse('recebedor-list')
        data = {
            'nome': 'Ana Silva',
            'email': 'ana@email.com',
            'telefone': '11966666666'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recebedor.objects.count(), 2)

    def test_list_itens(self):
        """Testa listagem de itens via API"""
        url = reverse('item-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_item(self):
        """Testa criação de item via API"""
        url = reverse('item-list')
        data = {
            'nome': 'Calça',
            'tipo': 'RO',
            'descricao': 'Calça jeans',
            'doador': self.doador.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 2)

    def test_unauthorized_access(self):
        """Testa acesso não autorizado à API"""
        self.client.force_authenticate(user=None)
        url = reverse('doacao-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED) 