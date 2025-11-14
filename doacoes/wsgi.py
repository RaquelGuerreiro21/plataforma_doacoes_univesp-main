"""
WSGI config for doacoes project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Configurar variáveis de ambiente
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "doacoes.settings")

# Inicializar aplicação
application = get_wsgi_application()
app = application
