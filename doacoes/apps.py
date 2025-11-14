from django.apps import AppConfig
from django.db.models.signals import post_migrate

def criar_usuario_admin(sender, **kwargs):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Verifica se já existe um usuário admin
    if not User.objects.filter(email='admin@admin.com').exists():
        # Cria o usuário administrador
        User.objects.create_user(
            email='admin@admin.com',
            password='admin123',
            nome_completo='Administrador',
            role='ADMIN'
        )
        print('Usuário administrador criado com sucesso!')
        print('Email: admin@admin.com')
        print('Senha: admin123')

class DoacoesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "doacoes"

    def ready(self):
        # Conecta o sinal post_migrate para criar o usuário admin
        post_migrate.connect(criar_usuario_admin, sender=self) 