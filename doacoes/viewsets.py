from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from .models import Doador, Recebedor, Item, Doacao
from .serializers import (
    DoadorSerializer, RecebedorSerializer, ItemSerializer, DoacaoSerializer,
    UserSerializer, CustomTokenObtainPairSerializer
)

User = get_user_model()

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role == 'ADMIN'

class IsGerenteUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.role in ['ADMIN', 'GERENTE']

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.get(email=request.data['email'])
            user.ultimo_acesso = timezone.now()
            user.save()
        return response

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def create_gerente(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(role='GERENTE')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request, pk=None):
        user = self.get_object()
        
        # Apenas o próprio usuário ou um admin pode alterar a senha
        if request.user.pk != user.pk and not request.user.role == 'ADMIN':
            return Response(
                {'error': 'Você não tem permissão para alterar a senha deste usuário.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # Validar senha atual
            if not request.data.get('old_password'):
                return Response(
                    {'old_password': 'A senha atual é obrigatória.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validar nova senha
            if not request.data.get('password'):
                return Response(
                    {'password': 'A nova senha é obrigatória.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not request.data.get('password2'):
                return Response(
                    {'password2': 'A confirmação da nova senha é obrigatória.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if request.data.get('password') != request.data.get('password2'):
                return Response(
                    {'password2': 'As senhas não conferem.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response({'message': 'Senha alterada com sucesso.'})
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class BaseModelViewSet(viewsets.ModelViewSet):
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DoadorViewSet(BaseModelViewSet):
    queryset = Doador.objects.all()
    serializer_class = DoadorSerializer
    permission_classes = [permissions.IsAuthenticated]

class RecebedorViewSet(BaseModelViewSet):
    queryset = Recebedor.objects.all()
    serializer_class = RecebedorSerializer
    permission_classes = [permissions.IsAuthenticated]

class ItemViewSet(BaseModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

class DoacaoViewSet(BaseModelViewSet):
    queryset = Doacao.objects.all()
    serializer_class = DoacaoSerializer
    permission_classes = [permissions.IsAuthenticated]
