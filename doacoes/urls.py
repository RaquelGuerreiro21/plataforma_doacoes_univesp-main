from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)
from .viewsets import (
    DoadorViewSet, 
    RecebedorViewSet, 
    ItemViewSet, 
    DoacaoViewSet, 
    UserViewSet,
    CustomTokenObtainPairView,
)
from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth.views import LogoutView
from django.views.decorators.csrf import ensure_csrf_cookie
from doacoes import views


router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'doadores', DoadorViewSet)
router.register(r'recebedores', RecebedorViewSet)
router.register(r'itens', ItemViewSet)
router.register(r'doacoes', DoacaoViewSet)


urlpatterns = [
    # Autenticação
    path('', ensure_csrf_cookie(views.login_view), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    
    # Área administrativa
    path('dashboard/', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),

    # Rotas protegidas
    path('doadores/', views.doador_list, name='doador_list'),
    path('recebedores/', views.recebedor_list, name='recebedor_list'),
    path('itens/', views.item_list, name='item_list'),
    path('doacoes/', views.doacao_list, name='doacao_list'),
    path('doacoes/nova/', views.doacao_wizard, name='doacao_wizard'),
    path('doacoes/<int:pk>/', views.doacao_detail, name='doacao_detail'),

    # API URLs
    path('api/wizard/doacoes/', views.doacao_wizard_api, name='doacao_wizard_api'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),

    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
