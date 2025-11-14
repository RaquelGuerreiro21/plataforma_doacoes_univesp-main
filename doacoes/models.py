from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('O e-mail é obrigatório'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser deve ter is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser deve ter is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrador'),
        ('GERENTE', 'Gerente'),
    ]

    username = None
    email = models.EmailField(_('endereço de email'), unique=True)
    nome_completo = models.CharField(_('nome completo'), max_length=255)
    role = models.CharField(_('função'), max_length=10, choices=ROLE_CHOICES, default='GERENTE')
    data_criacao = models.DateTimeField(_('data de criação'), auto_now_add=True)
    ultimo_acesso = models.DateTimeField(_('último acesso'), null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nome_completo']

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')

    def __str__(self):
        return self.email

class Doador(models.Model):
    nome = models.CharField(_('nome'), max_length=255)
    email = models.EmailField(_('email'), blank=True, null=True)
    telefone = models.CharField(_('telefone'), max_length=20, blank=True, null=True)
    endereco = models.CharField(_('endereço'), max_length=255, blank=True, null=True)
    observacoes = models.TextField(_('observações'), blank=True)
    data_cadastro = models.DateTimeField(_('data de cadastro'), auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(_('última atualização'), auto_now=True)

    class Meta:
        verbose_name = _('doador')
        verbose_name_plural = _('doadores')
        ordering = ['nome']

    def clean(self):
        if not self.nome:
            raise ValidationError({'nome': _('O nome do doador é obrigatório.')})
        
        # Garante que pelo menos um campo de contato seja preenchido
        if not self.email and not self.telefone:
            raise ValidationError(_('É necessário fornecer pelo menos um contato (email ou telefone)'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Recebedor(models.Model):
    nome = models.CharField(_('nome'), max_length=255)
    email = models.EmailField(_('email'), blank=True, null=True)
    telefone = models.CharField(_('telefone'), max_length=20, blank=True, null=True)
    endereco = models.CharField(_('endereço'), max_length=255, blank=True, null=True)
    observacoes = models.TextField(_('observações'), blank=True)
    data_cadastro = models.DateTimeField(_('data de cadastro'), auto_now_add=True)
    ultima_atualizacao = models.DateTimeField(_('última atualização'), auto_now=True)

    class Meta:
        verbose_name = _('recebedor')
        verbose_name_plural = _('recebedores')
        ordering = ['nome']

    def clean(self):
        if not self.nome:
            raise ValidationError({'nome': _('O nome do recebedor é obrigatório.')})
        
        # Garante que pelo menos um campo de contato seja preenchido
        if not self.email and not self.telefone:
            raise ValidationError(_('É necessário fornecer pelo menos um contato (email ou telefone)'))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nome

class Item(models.Model):
    TIPO_CHOICES = [
        ('RO', 'Roupas'),
        ('MO', 'Móveis'),
        ('CO', 'Comidas'),
        ('PE', 'Perecíveis'),
        ('EL', 'Eletrônicos'),
        ('LI', 'Livros'),
        ('BR', 'Brinquedos'),
        ('UD', 'Utensílios Domésticos'),
        ('MS', 'Material Escolar'),
        ('FE', 'Ferramentas'),
        ('JR', 'Jornais/Revistas'),
        ('CB', 'Cobertores'),
        ('CA', 'Calçados'),
        ('AC', 'Acessórios'),
        ('IM', 'Instrumentos Musicais'),
        ('PH', 'Produtos de Higiene'),
        ('ME', 'Medicamentos'),
        ('VE', 'Veículos'),
        ('ED', 'Eletrodomésticos'),
        ('MC', 'Materiais de Construção'),
        ('OU', 'Outros'),
    ]

    nome = models.CharField(_('nome'), max_length=255)
    tipo = models.CharField(_('tipo'), max_length=2, choices=TIPO_CHOICES)
    descricao = models.TextField(_('descrição'), blank=True)
    disponivel = models.BooleanField(_('disponível'), default=True)
    foto = models.FileField(_('foto'), upload_to='itens/', null=True, blank=True)
    doador = models.ForeignKey(Doador, on_delete=models.SET_NULL, null=True, blank=True, related_name='itens', verbose_name=_('doador'))

    class Meta:
        verbose_name = _('item')
        verbose_name_plural = _('itens')
        ordering = ['nome']

    def clean(self):
        if not self.nome:
            raise ValidationError({'nome': _('O nome do item é obrigatório.')})
        if not self.tipo:
            raise ValidationError({'tipo': _('O tipo do item é obrigatório.')})
        if self.tipo not in dict(self.TIPO_CHOICES):
            raise ValidationError({'tipo': _('Tipo inválido. Escolha uma das opções disponíveis.')})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nome} - {self.get_tipo_display()}"

class Doacao(models.Model):
    doador = models.ForeignKey(Doador, on_delete=models.CASCADE, related_name='doacoes')
    recebedor = models.ForeignKey('Recebedor', on_delete=models.CASCADE, related_name='recebimentos', null=True, blank=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    data = models.DateTimeField(_('data da doação'), auto_now_add=True)
    observacoes = models.TextField(_('observações'), blank=True)

    class Meta:
        verbose_name = _('doação')
        verbose_name_plural = _('doações')
        ordering = ['-data']

    def clean(self):
        if not self.doador:
            raise ValidationError({'doador': _('O doador é obrigatório.')})
        
        if not self.item and not self.valor:
            raise ValidationError(_('É necessário fornecer um item ou um valor para a doação'))
        
        if self.item and self.valor:
            raise ValidationError(_('Uma doação não pode ter item e valor monetário simultaneamente'))
        
        if self.valor and self.valor <= 0:
            raise ValidationError({'valor': _('O valor da doação deve ser maior que zero')})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.item:
            return f"Doação de {self.item} por {self.doador}"
        else:
            return f"Doação de R$ {self.valor} por {self.doador}"
