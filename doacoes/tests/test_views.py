from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from doacoes.models import Doador, Recebedor, Item, Doacao
from rest_framework.test import APIClient
import json

User = get_user_model()

class ViewsTestCase(TestCase):
    def setUp(self):
        # Criar usuário para autenticação
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nome_completo='Test User'
        )
        
        # Adicionar todas as permissões necessárias
        for model in [Doacao, Item, Doador, Recebedor]:
            content_type = ContentType.objects.get_for_model(model)
            for action in ['add', 'change', 'delete', 'view']:
                permission = Permission.objects.get(
                    content_type=content_type,
                    codename=f'{action}_{model._meta.model_name}'
                )
                self.user.user_permissions.add(permission)
        
        # Cliente regular para views normais
        self.client = Client()
        self.client.login(email='test@example.com', password='testpass123')
        
        # Cliente API para testes de API
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.user)

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

    def test_dashboard_view(self):
        """Testa a view do dashboard"""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard.html')
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Nova Doação')

    def test_doacao_list_view(self):
        """Testa a view de lista de doações"""
        response = self.client.get(reverse('doacao_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doacao_list.html')
        self.assertContains(response, 'Doações')
        self.assertContains(response, self.doador.nome)
        self.assertContains(response, self.recebedor.nome)

    def test_doacao_wizard_view(self):
        """Testa a view do wizard de doações"""
        response = self.client.get(reverse('doacao_wizard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doacao_wizard.html')
        self.assertContains(response, 'Nova Doação')
        self.assertContains(response, 'Registro do Item')
        self.assertContains(response, 'Registro do Doador')
        self.assertContains(response, 'Registro do Recebedor')
        self.assertContains(response, 'Confirmação')

    def test_doacao_wizard_api(self):
        """Testa a API do wizard de doações"""
        data = {
            'item_nome': 'Calça',
            'item_tipo': 'RO',
            'item_descricao': 'Calça jeans',
            'doador_tipo': 'novo',
            'doador_nome': 'Pedro Silva',
            'doador_email': 'pedro@email.com',
            'doador_telefone': '',
            'doador_endereco': '',
            'recebedor_tipo': 'novo',
            'recebedor_nome': 'Ana Santos',
            'recebedor_email': 'ana@email.com',
            'recebedor_telefone': '',
            'recebedor_endereco': ''
        }
        
        # Verifica se o usuário tem todas as permissões necessárias
        required_permissions = [
            'doacoes.add_doacao',
            'doacoes.add_item',
            'doacoes.add_doador',
            'doacoes.add_recebedor'
        ]
        for perm in required_permissions:
            self.assertTrue(
                self.user.has_perm(perm),
                f"Usuário não tem a permissão {perm}"
            )
        
        response = self.api_client.post(
            reverse('doacao_wizard_api'),
            data=data,
            format='json'
        )
        
        # Verifica o status code e imprime detalhes em caso de erro
        if response.status_code != 201:
            print(f"Status code: {response.status_code}")
            print(f"Response content: {response.content}")
            print(f"Response headers: {response.headers}")
        
        self.assertEqual(response.status_code, 201)
        
        # Verificar se os objetos foram criados
        self.assertTrue(Item.objects.filter(nome='Calça').exists())
        self.assertTrue(Doador.objects.filter(nome='Pedro Silva').exists())
        self.assertTrue(Recebedor.objects.filter(nome='Ana Santos').exists())
        
    def test_doador_list_view(self):
        """Testa a view de lista de doadores"""
        response = self.client.get(reverse('doador_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'doador_list.html')
        self.assertContains(response, 'Doadores')
        self.assertContains(response, self.doador.nome)

    def test_recebedor_list_view(self):
        """Testa a view de lista de recebedores"""
        response = self.client.get(reverse('recebedor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recebedor_list.html')
        self.assertContains(response, 'Recebedores')
        self.assertContains(response, self.recebedor.nome)

    def test_item_list_view(self):
        """Testa a view de lista de itens"""
        response = self.client.get(reverse('item_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'item_list.html')
        self.assertContains(response, 'Itens')
        self.assertContains(response, self.item.nome)

    def test_unauthorized_access(self):
        """Testa acesso não autorizado"""
        self.client.logout()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redireciona para login
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('dashboard')}") 