from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from doacoes.models import Doador, Recebedor, Item, Doacao

User = get_user_model()

class UserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            nome_completo='Test User'
        )

    def test_criacao_usuario(self):
        """Testa a criação de um usuário"""
        self.assertTrue(isinstance(self.user, User))
        self.assertEqual(self.user.__str__(), 'test@example.com')

    def test_campos_usuario(self):
        """Testa os campos do usuário"""
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.nome_completo, 'Test User')
        self.assertEqual(self.user.role, 'GERENTE')  # Valor padrão
        self.assertTrue(isinstance(self.user.data_criacao, timezone.datetime))

    def test_criacao_superuser(self):
        """Testa a criação de um superusuário"""
        admin = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            nome_completo='Admin User'
        )
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.role, 'ADMIN')

class DoadorTests(TestCase):
    def setUp(self):
        self.doador = Doador.objects.create(
            nome='João Silva',
            email='joao@email.com',
            telefone='11999999999',
            endereco='Rua Teste, 123',
            observacoes='Observação teste'
        )

    def test_criacao_doador(self):
        """Testa a criação de um doador"""
        self.assertTrue(isinstance(self.doador, Doador))
        self.assertEqual(self.doador.__str__(), 'João Silva')

    def test_campos_doador(self):
        """Testa os campos do doador"""
        self.assertEqual(self.doador.nome, 'João Silva')
        self.assertEqual(self.doador.email, 'joao@email.com')
        self.assertEqual(self.doador.telefone, '11999999999')
        self.assertEqual(self.doador.endereco, 'Rua Teste, 123')
        self.assertEqual(self.doador.observacoes, 'Observação teste')
        self.assertTrue(isinstance(self.doador.data_cadastro, timezone.datetime))

class RecebedorTests(TestCase):
    def setUp(self):
        self.recebedor = Recebedor.objects.create(
            nome='Maria Santos',
            email='maria@email.com',
            telefone='11988888888',
            endereco='Rua Teste, 456',
            observacoes='Observação teste'
        )

    def test_criacao_recebedor(self):
        """Testa a criação de um recebedor"""
        self.assertTrue(isinstance(self.recebedor, Recebedor))
        self.assertEqual(self.recebedor.__str__(), 'Maria Santos')

    def test_campos_recebedor(self):
        """Testa os campos do recebedor"""
        self.assertEqual(self.recebedor.nome, 'Maria Santos')
        self.assertEqual(self.recebedor.email, 'maria@email.com')
        self.assertEqual(self.recebedor.telefone, '11988888888')
        self.assertEqual(self.recebedor.endereco, 'Rua Teste, 456')
        self.assertEqual(self.recebedor.observacoes, 'Observação teste')
        self.assertTrue(isinstance(self.recebedor.data_cadastro, timezone.datetime))

class ItemTests(TestCase):
    def setUp(self):
        self.doador = Doador.objects.create(nome='João Silva')
        self.item = Item.objects.create(
            nome='Camiseta',
            tipo='RO',
            descricao='Camiseta branca tamanho M',
            disponivel=True,
            doador=self.doador
        )

    def test_criacao_item(self):
        """Testa a criação de um item"""
        self.assertTrue(isinstance(self.item, Item))
        self.assertEqual(self.item.__str__(), 'Camiseta - Roupas')

    def test_campos_item(self):
        """Testa os campos do item"""
        self.assertEqual(self.item.nome, 'Camiseta')
        self.assertEqual(self.item.tipo, 'RO')
        self.assertEqual(self.item.get_tipo_display(), 'Roupas')
        self.assertEqual(self.item.descricao, 'Camiseta branca tamanho M')
        self.assertTrue(self.item.disponivel)
        self.assertEqual(self.item.doador, self.doador)

class DoacaoTests(TestCase):
    def setUp(self):
        self.doador = Doador.objects.create(nome='João Silva')
        self.recebedor = Recebedor.objects.create(nome='Maria Santos')
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

    def test_criacao_doacao(self):
        """Testa a criação de uma doação"""
        self.assertTrue(isinstance(self.doacao, Doacao))
        self.assertEqual(self.doacao.__str__(), 'Doação de Camiseta - Roupas por João Silva')

    def test_campos_doacao(self):
        """Testa os campos da doação"""
        self.assertEqual(self.doacao.doador, self.doador)
        self.assertEqual(self.doacao.recebedor, self.recebedor)
        self.assertEqual(self.doacao.item, self.item)
        self.assertTrue(isinstance(self.doacao.data, timezone.datetime))

    def test_doacao_valor(self):
        """Testa doação com valor monetário"""
        doacao_valor = Doacao.objects.create(
            doador=self.doador,
            recebedor=self.recebedor,
            valor=100.00
        )
        self.assertEqual(doacao_valor.__str__(), 'Doação de R$ 100.0 por João Silva') 