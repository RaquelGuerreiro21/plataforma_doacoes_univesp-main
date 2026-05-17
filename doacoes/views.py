from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.http import JsonResponse
from .models import User, Doador, Recebedor, Item, Doacao
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils import timezone
import json

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not email or not password:
            messages.error(request, 'E-mail e senha são obrigatórios.')
            return render(request, 'login.html', status=400)
        
        try:
            user = authenticate(request, email=email, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Login realizado com sucesso!')
                next_url = 'user_list' if user.role == 'ADMIN' else 'dashboard'
                return redirect(next_url)
            else:
                messages.error(request, 'E-mail ou senha inválidos.')
                return render(request, 'login.html', status=400)
                
        except Exception as e:
            logger.error(f"Erro no login: {str(e)}")
            messages.error(request, 'Erro ao realizar login. Tente novamente.')
            return render(request, 'login.html', status=400)
    
    return render(request, 'login.html')

def is_admin(user):
    return user.role == 'ADMIN'

@login_required
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.all().order_by('-role', 'nome_completo')
    return render(request, 'user_list.html', {'users': users})

@login_required
def dashboard(request):
    try:
        # --- Totais gerais ---
        total_doacoes = Doacao.objects.count()
        total_doadores = Doador.objects.count()
        total_recebedores = Recebedor.objects.count()
        total_itens = Item.objects.count()

        # --- Financeiro ---
        total_dinheiro = Doacao.objects.filter(valor__isnull=False).aggregate(
            total=Sum('valor')
        )['total'] or 0

        total_doacoes_dinheiro = Doacao.objects.filter(valor__isnull=False).count()
        total_doacoes_item = Doacao.objects.filter(item__isnull=False).count()

        # --- Doações dos últimos 6 meses (para gráfico de linha) ---
        seis_meses_atras = timezone.now() - timedelta(days=180)
        doacoes_por_mes = (
            Doacao.objects
            .filter(data__gte=seis_meses_atras)
            .annotate(mes=TruncMonth('data'))
            .values('mes')
            .annotate(total=Count('id'), valor_total=Sum('valor'))
            .order_by('mes')
        )

        meses_labels = []
        meses_contagem = []
        meses_valores = []
        for d in doacoes_por_mes:
            meses_labels.append(d['mes'].strftime('%b/%Y'))
            meses_contagem.append(d['total'])
            meses_valores.append(float(d['valor_total'] or 0))

        # --- Top 5 doadores ---
        top_doadores = (
            Doador.objects
            .annotate(total_doacoes=Count('doacoes'))
            .order_by('-total_doacoes')[:5]
        )

        # --- Top 5 recebedores ---
        top_recebedores = (
            Recebedor.objects
            .annotate(total_recebimentos=Count('recebimentos'))
            .order_by('-total_recebimentos')[:5]
        )

        # --- Itens por tipo (para gráfico de pizza) ---
        itens_por_tipo = (
            Item.objects
            .values('tipo')
            .annotate(total=Count('id'))
            .order_by('-total')[:6]
        )
        tipo_dict = dict(Item.TIPO_CHOICES)
        itens_tipos_labels = [tipo_dict.get(i['tipo'], i['tipo']) for i in itens_por_tipo]
        itens_tipos_valores = [i['total'] for i in itens_por_tipo]

        # --- Doações recentes ---
        doacoes_recentes = Doacao.objects.select_related('doador', 'recebedor', 'item').order_by('-data')[:5]

        context = {
            'total_doacoes': total_doacoes,
            'total_doadores': total_doadores,
            'total_recebedores': total_recebedores,
            'total_itens': total_itens,
            'total_dinheiro': total_dinheiro,
            'total_doacoes_dinheiro': total_doacoes_dinheiro,
            'total_doacoes_item': total_doacoes_item,
            'meses_labels': json.dumps(meses_labels),
            'meses_contagem': json.dumps(meses_contagem),
            'meses_valores': json.dumps(meses_valores),
            'top_doadores': top_doadores,
            'top_recebedores': top_recebedores,
            'itens_tipos_labels': json.dumps(itens_tipos_labels),
            'itens_tipos_valores': json.dumps(itens_tipos_valores),
            'doacoes_recentes': doacoes_recentes,
        }
        return render(request, 'dashboard.html', context)
    except Exception as e:
        logger.error(f"Erro no dashboard: {str(e)}")
        messages.error(request, 'Erro ao carregar o dashboard.')
        return render(request, 'dashboard.html', {'error': True})

@login_required
def doador_list(request):
    try:
        doadores = Doador.objects.all().order_by('nome')
        return render(request, 'doador_list.html', {'doadores': doadores})
    except Exception as e:
        logger.error(f"Erro na lista de doadores: {str(e)}")
        messages.error(request, 'Erro ao carregar a lista de doadores.')
        return render(request, 'doador_list.html', {'error': True})

@login_required
def recebedor_list(request):
    try:
        recebedores = Recebedor.objects.all().order_by('nome')
        return render(request, 'recebedor_list.html', {'recebedores': recebedores})
    except Exception as e:
        logger.error(f"Erro na lista de recebedores: {str(e)}")
        messages.error(request, 'Erro ao carregar a lista de recebedores.')
        return render(request, 'recebedor_list.html', {'error': True})

@login_required
def item_list(request):
    try:
        itens = Item.objects.all().order_by('nome')
        doacoes = Doacao.objects.filter(valor__isnull=False).order_by('-data')
        doadores = Doador.objects.all().order_by('nome')
        recebedores = Recebedor.objects.all().order_by('nome')
        
        logger.info(f"Listando {itens.count()} itens e {doacoes.count()} doações em dinheiro")
        
        return render(request, 'item_list.html', {
            'itens': itens,
            'doacoes': doacoes,
            'doadores': doadores,
            'recebedores': recebedores,
            'tipos_item': Item.TIPO_CHOICES
        })
    except Exception as e:
        logger.error(f"Erro na lista de itens: {str(e)}", exc_info=True)
        messages.error(request, 'Erro ao carregar a lista de itens.')
        return render(request, 'item_list.html', {'error': True})

@login_required
def doacao_list(request):
    try:
        doacoes = Doacao.objects.all().order_by('-data')
        doadores = Doador.objects.all().order_by('nome')
        recebedores = Recebedor.objects.all().order_by('nome')
        itens_disponiveis = Item.objects.filter(disponivel=True).order_by('nome')
        
        context = {
            'doacoes': doacoes,
            'doadores': doadores,
            'recebedores': recebedores,
            'itens_disponiveis': itens_disponiveis,
        }
        return render(request, 'doacao_list.html', context)
    except Exception as e:
        logger.error(f"Erro na lista de doações: {str(e)}")
        messages.error(request, 'Erro ao carregar a lista de doações.')
        return render(request, 'doacao_list.html', {'error': True})

@login_required
def doacao_wizard(request):
    """View para o wizard de criação de doações em etapas."""
    try:
        context = {
            'tipos_item': Item.TIPO_CHOICES,
            'doadores': Doador.objects.all().order_by('nome'),
            'recebedores': Recebedor.objects.all().order_by('nome'),
        }
        return render(request, 'doacao_wizard.html', context)
    except Exception as e:
        logger.error(f"Erro no wizard de doações: {str(e)}")
        messages.error(request, 'Erro ao carregar o formulário de doação.')
        return redirect('doacao_list')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_protect
def doacao_wizard_api(request):
    """API endpoint para processar o wizard de doações."""
    if request.user.role not in ['ADMIN', 'GERENTE']:
        return Response(
            {'error': 'Permissão negada. Apenas administradores e gerentes podem registrar doações.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        data = request.data
        tipo_doacao = data.get('tipo_doacao')
        
        # Processa o doador
        if data.get('doador_tipo') == 'existente':
            doador = Doador.objects.get(id=data.get('doador_id'))
        else:
            doador = Doador.objects.create(
                nome=data.get('doador_nome'),
                email=data.get('doador_email'),
                telefone=data.get('doador_telefone'),
                endereco=data.get('doador_endereco')
            )
        
        # Processa o recebedor
        recebedor = None
        if data.get('recebedor_tipo') == 'existente' and data.get('recebedor_id'):
            recebedor = Recebedor.objects.get(id=data.get('recebedor_id'))
        elif data.get('recebedor_tipo') == 'novo' and data.get('recebedor_nome'):
            recebedor = Recebedor.objects.create(
                nome=data.get('recebedor_nome'),
                email=data.get('recebedor_email'),
                telefone=data.get('recebedor_telefone'),
                endereco=data.get('recebedor_endereco')
            )

        # Cria a doação baseada no tipo
        if tipo_doacao == 'dinheiro':
            valor = data.get('valor')
            try:
                valor_str = str(valor).replace('.', '').replace(',', '.')
                valor_float = float(valor_str)
                if valor_float <= 0:
                    return Response(
                        {'error': 'O valor da doação deve ser maior que zero'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (TypeError, ValueError):
                return Response(
                    {'error': 'Valor inválido. Use o formato: 1000.00'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            doacao = Doacao.objects.create(
                doador=doador,
                recebedor=recebedor,
                valor=valor_float
            )
        else:  # tipo_doacao == 'item'
            item_data = {
                'nome': data.get('item_nome'),
                'tipo': data.get('item_tipo'),
                'descricao': data.get('item_descricao'),
                'disponivel': True,
                'doador': doador
            }
            
            if request.FILES and 'item_foto' in request.FILES:
                item_data['foto'] = request.FILES['item_foto']
            
            item = Item.objects.create(**item_data)
            
            doacao = Doacao.objects.create(
                item=item,
                doador=doador,
                recebedor=recebedor
            )
            
            if recebedor:
                item.disponivel = False
                item.save()
        
        return Response({'id': doacao.id}, status=status.HTTP_201_CREATED)
        
    except Doador.DoesNotExist:
        return Response({'error': 'Doador não encontrado'}, status=status.HTTP_400_BAD_REQUEST)
    except Recebedor.DoesNotExist:
        return Response({'error': 'Recebedor não encontrado'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Erro ao processar wizard de doação: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@login_required
def doacao_detail(request, pk):
    """View para exibir os detalhes de uma doação específica."""
    try:
        doacao = Doacao.objects.get(pk=pk)
        return render(request, 'doacao_detail.html', {'doacao': doacao})
    except Doacao.DoesNotExist:
        messages.error(request, 'Doação não encontrada.')
        return redirect('doacao_list')
    except Exception as e:
        logger.error(f"Erro ao exibir detalhes da doação: {str(e)}")
        messages.error(request, 'Erro ao carregar os detalhes da doação.')
        return redirect('doacao_list')