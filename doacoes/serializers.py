from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from .models import Doador, Recebedor, Item, Doacao

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        token['nome_completo'] = user.nome_completo
        return token

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=False)
    old_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'nome_completo', 'password', 'password2', 'old_password', 'role', 'data_criacao', 'ultimo_acesso')
        read_only_fields = ('id', 'data_criacao', 'ultimo_acesso')
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        # Validação para criação de usuário
        if self.instance is None and 'password2' not in attrs:
            raise serializers.ValidationError({"password2": "É necessário confirmar a senha."})
        
        # Validação de confirmação de senha na criação
        if 'password2' in attrs:
            if attrs['password'] != attrs['password2']:
                raise serializers.ValidationError({"password2": "As senhas não conferem."})
            attrs.pop('password2')
            
        # Validação para atualização de senha
        if self.instance and 'old_password' in attrs:
            if not self.instance.check_password(attrs['old_password']):
                raise serializers.ValidationError({"old_password": "Senha atual incorreta."})
            attrs.pop('old_password')
            
        return attrs

    def create(self, validated_data):
        if 'password2' in validated_data:
            validated_data.pop('password2')
            
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            nome_completo=validated_data['nome_completo'],
            role=validated_data.get('role', 'GERENTE')
        )
        return user

    def update(self, instance, validated_data):
        # Remove campos de senha se não estiverem sendo atualizados
        password = validated_data.pop('password', None)
        
        # Atualiza os outros campos
        for attr, value in validated_data.items():
            if attr not in ['password2', 'old_password']:
                setattr(instance, attr, value)
        
        # Atualiza a senha se fornecida
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance

class DoadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doador
        fields = '__all__'

class RecebedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recebedor
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'

    def validate_tipo(self, value):
        if value not in dict(Item.TIPO_CHOICES):
            raise serializers.ValidationError(
                f"Tipo inválido. Escolha entre: {', '.join([f'{k} ({v})' for k, v in Item.TIPO_CHOICES])}"
            )
        return value

    def validate(self, data):
        if not data.get('nome'):
            raise serializers.ValidationError({'nome': 'O nome do item é obrigatório'})
        
        if not data.get('tipo'):
            raise serializers.ValidationError({'tipo': 'O tipo do item é obrigatório'})

        # Validar tamanho máximo da foto (se fornecida)
        foto = data.get('foto')
        if foto and hasattr(foto, 'size'):
            max_size = 5 * 1024 * 1024  # 5MB
            if foto.size > max_size:
                raise serializers.ValidationError({
                    'foto': f'A foto não pode ter mais que 5MB. Tamanho atual: {foto.size/1024/1024:.1f}MB'
                })

        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Erro ao criar item: {str(e)}")

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Erro ao atualizar item: {str(e)}")

class DoacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doacao
        fields = '__all__'

    def validate(self, data):
        # Validar se foi fornecido item OU valor (não ambos)
        if 'item' in data and 'valor' in data:
            if data['item'] is not None and data['valor'] is not None:
                raise serializers.ValidationError(
                    "Uma doação não pode ter item e valor monetário simultaneamente"
                )
        
        # Validar se pelo menos um dos dois foi fornecido
        if ('item' not in data or data['item'] is None) and ('valor' not in data or data['valor'] is None):
            raise serializers.ValidationError(
                "É necessário fornecer um item ou um valor para a doação"
            )

        # Validar valor monetário
        if 'valor' in data and data['valor'] is not None:
            if data['valor'] <= 0:
                raise serializers.ValidationError({
                    'valor': 'O valor da doação deve ser maior que zero'
                })

        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Erro ao criar doação: {str(e)}")

    def update(self, instance, validated_data):
        try:
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError(f"Erro ao atualizar doação: {str(e)}")
