from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import socket
from django.test.utils import override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
import time

User = get_user_model()

class TesteInterface(LiveServerTestCase):
    host = '0.0.0.0'

    @classmethod
    def setUpClass(cls):
        # Obtém o IP da máquina host
        cls.host_ip = socket.gethostbyname(socket.gethostname())
        # Configura ALLOWED_HOSTS
        cls.settings_manager = override_settings(
            ALLOWED_HOSTS=['*'],
            CSRF_COOKIE_SECURE=False,
            CSRF_COOKIE_HTTPONLY=False,
            SESSION_COOKIE_SECURE=False
        )
        cls.settings_manager.enable()
        super().setUpClass()

        # Cria um usuário para teste
        cls.user = User.objects.create_user(
            email='teste@teste.com',
            password='senha123',
            nome_completo='Usuário Teste',
            role='ADMIN'
        )

        # Configura o Chrome em modo headless
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')

        # Inicializa o Chrome
        service = Service(ChromeDriverManager().install())
        cls.selenium = webdriver.Chrome(service=service, options=chrome_options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        cls.settings_manager.disable()
        super().tearDownClass()

    def login(self):
        # Usa o IP do host ao invés de localhost
        url = self.live_server_url.replace('0.0.0.0', self.host_ip)
        
        # Primeiro acesso para obter o cookie CSRF
        self.selenium.get(f'{url}/')
        time.sleep(1)  # Espera um segundo para garantir que o cookie foi definido
        
        # Verifica se a página de login foi carregada
        titulo = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h2'))
        )
        self.assertEqual('Bem-vindo de volta!', titulo.text)
        
        # Preenche o formulário de login
        email_input = self.selenium.find_element(By.NAME, 'email')
        password_input = self.selenium.find_element(By.NAME, 'password')
        
        email_input.clear()
        password_input.clear()
        
        email_input.send_keys('teste@teste.com')
        password_input.send_keys('senha123')
        
        # Espera até que o botão esteja clicável
        submit_button = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        submit_button.click()
        
        # Espera até que o dashboard seja carregado
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'navbar-brand'))
        )

    def test_pagina_inicial(self):
        self.login()
        # Usa o IP do host ao invés de localhost
        url = self.live_server_url.replace('0.0.0.0', self.host_ip)
        self.selenium.get(f'{url}/dashboard/')
        
        # Espera até que o título seja carregado
        titulo = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h2'))
        )
        self.assertEqual('Dashboard', titulo.text)

    def test_criar_doacao(self):
        self.login()
        # Usa o IP do host ao invés de localhost
        url = self.live_server_url.replace('0.0.0.0', self.host_ip)
        self.selenium.get(f'{url}/doacoes/nova/')
        
        # Espera até que o formulário seja carregado
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'nome'))
        )
        
        # Preenche o formulário
        nome_input = self.selenium.find_element(By.NAME, 'nome')
        valor_input = self.selenium.find_element(By.NAME, 'valor')
        forma_pagamento_input = self.selenium.find_element(By.NAME, 'forma_pagamento')
        
        nome_input.clear()
        valor_input.clear()
        forma_pagamento_input.clear()
        
        nome_input.send_keys('Doador Teste')
        valor_input.send_keys('100')
        forma_pagamento_input.send_keys('PIX')
        
        # Espera até que o botão esteja clicável
        submit_button = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]'))
        )
        submit_button.click()
        
        # Espera pela mensagem de sucesso
        mensagem = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'mensagem-sucesso'))
        )
        self.assertIn('Doação registrada com sucesso', mensagem.text) 