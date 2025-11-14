from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Cria um usuário administrador'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='admin@admin.com', help='Email do administrador')
        parser.add_argument('--password', type=str, default='admin123', help='Senha do administrador')
        parser.add_argument('--nome', type=str, default='Administrador', help='Nome completo do administrador')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        nome = options['nome']

        try:
            # Verifica se o usuário já existe
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'Usuário com email {email} já existe.')
                )
                return

            # Cria o usuário administrador
            admin = User.objects.create_user(
                email=email,
                password=password,
                nome_completo=nome,
                role='ADMIN'
            )

            self.stdout.write(
                self.style.SUCCESS(f'Usuário administrador criado com sucesso!\n'
                                 f'Email: {email}\n'
                                 f'Senha: {password}\n'
                                 f'Nome: {nome}')
            )

        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar usuário: {str(e)}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro inesperado: {str(e)}')
            ) 