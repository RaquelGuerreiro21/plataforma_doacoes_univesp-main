# 🤝 Sistema de Gestão de Doações

> Projeto Integrador — Universidade Virtual do Estado de São Paulo (UNIVESP)

Plataforma web desenvolvida para uma instituição religiosa sem fins lucrativos, com o objetivo de digitalizar e organizar o gerenciamento de doações recebidas e distribuídas pela instituição.

---

## 📋 Sobre o Projeto

Este sistema foi desenvolvido como Projeto Integrador (PI) da UNIVESP, em parceria com uma igreja que realiza trabalhos sociais na comunidade. Antes da plataforma, o controle de doações era feito de forma manual, dificultando o acompanhamento e a transparência do processo.

Com o sistema, a instituição pode:

- Cadastrar e gerenciar **doadores**
- Cadastrar e gerenciar **recebedores**
- Registrar **itens** disponíveis para doação
- Criar e acompanhar **doações** realizadas
- Ter uma visão geral pelo **Dashboard**
- Controlar acessos com sistema de **autenticação de usuários**

---

## 🚀 Acesso à Plataforma

A aplicação está disponível em produção:

🔗 **[plataforma-doacoes-univesp.vercel.app](https://plataforma-doacoes-univesp.vercel.app)**

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
|---|---|
| **Python 3.12** | Linguagem principal |
| **Django 5.2** | Framework web back-end |
| **Django REST Framework** | API REST |
| **PostgreSQL (Neon)** | Banco de dados em produção |
| **Vercel** | Deploy e hospedagem |
| **WhiteNoise** | Servir arquivos estáticos |
| **JWT (SimpleJWT)** | Autenticação via token |
| **python-dotenv** | Gerenciamento de variáveis de ambiente |

---

## ⚙️ Como Rodar Localmente

### Pré-requisitos

- Python 3.12+
- Git

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/RaquelGuerreiro21/plataforma_doacoes_univesp-main.git
cd plataforma_doacoes_univesp-main

# 2. Crie e ative o ambiente virtual
python -m venv .venv

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Linux/Mac
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
# Crie um arquivo .env na raiz do projeto com base no .env-example
# Adicione sua DATABASE_URL do Neon (ou use SQLite para testes locais)

# 5. Rode as migrações
python manage.py migrate

# 6. Crie um usuário administrador
python manage.py createadmin

# 7. Inicie o servidor
python manage.py runserver
```

Acesse em: `http://localhost:8000`

---

## 🔐 Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
SECRET_KEY=sua_secret_key_aqui
DEBUG=True
DATABASE_URL=postgresql://usuario:senha@host/banco?sslmode=require
```

> ⚠️ Nunca compartilhe o arquivo `.env` nem o suba para o repositório.

---

## 🗂️ Estrutura do Projeto

```
plataforma_doacoes_univesp/
├── doacoes/               # App principal
│   ├── management/        # Comandos customizados (createadmin)
│   ├── migrations/        # Migrações do banco de dados
│   ├── models.py          # Modelos: User, Doador, Recebedor, Item, Doacao
│   ├── views.py           # Views e endpoints da API
│   ├── urls.py            # Rotas da aplicação
│   └── settings.py        # Configurações do Django
├── templates/             # Templates HTML
├── staticfiles_build/     # Arquivos estáticos compilados
├── requirements.txt       # Dependências do projeto
├── vercel.json            # Configuração de deploy na Vercel
└── manage.py
```

---

## 👥 Equipe

Projeto desenvolvido por um grupo de 5 estudantes do curso de **Tecnologia em Análise e Desenvolvimento de Sistemas** da UNIVESP, como parte do Projeto Integrador do curso.

---

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos e para apoiar o trabalho social da instituição parceira. Todos os direitos reservados aos desenvolvedores e à UNIVESP.

---

<p align="center">Desenvolvido com ❤️ por estudantes da UNIVESP</p>
