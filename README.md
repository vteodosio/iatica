# 🐯 IÁtica Kids
### Ética e Inteligência Artificial para a Educação Básica

Plataforma web interativa para professores e alunos explorarem juntos o mundo da IA com responsabilidade, criatividade e diversão.

---

## 📁 Estrutura do Projeto

```
iatica_kids/                        ← Raiz do projeto
│
├── manage.py                       ← Utilitário de gestão Django
├── requirements.txt                ← Dependências Python
├── .env.example                    ← Modelo de variáveis de ambiente
│
├── iatica_kids/                    ← Configurações principais Django
│   ├── __init__.py
│   ├── settings.py                 ← Configurações (BD, apps, middleware)
│   ├── urls.py                     ← Roteamento principal
│   └── wsgi.py                     ← Entry point de produção
│
├── apps/                           ← Aplicações Django
│   │
│   ├── accounts/                   ← Autenticação e usuários
│   │   ├── models.py               ← User customizado (Professor / Aluno)
│   │   ├── views.py                ← Login, registro, dashboard professor
│   │   ├── forms.py                ← Formulários de cadastro e login
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── groups/                     ← Grupos de estudo
│   │   ├── models.py               ← GrupoEstudo, MembroGrupo
│   │   ├── views.py                ← Criar grupo, área do aluno, sala de estudo
│   │   └── urls.py
│   │
│   ├── content/                    ← Lições e progresso
│   │   ├── models.py               ← Licao, ProgressoLicao
│   │   ├── views.py                ← Detalhe da lição, marcar como lida
│   │   ├── urls.py
│   │   └── management/
│   │       └── commands/
│   │           └── seed_data.py    ← Popula BD com lições e perguntas
│   │
│   ├── quiz/                       ← Sistema de quiz
│   │   ├── models.py               ← Pergunta, Alternativa, Quiz, Tentativa
│   │   ├── views.py                ← Iniciar quiz, submeter, resultado
│   │   ├── urls.py
│   │   └── templatetags/
│   │       └── quiz_tags.py        ← Tags customizadas para templates
│   │
│   └── reports/                    ← Relatórios
│       ├── views.py                ← Relatório web + geração de PDF
│       └── urls.py
│
├── templates/                      ← Templates HTML
│   ├── base.html                   ← Layout base com navbar e design system
│   ├── home.html                   ← Página inicial
│   ├── accounts/
│   │   ├── login.html
│   │   ├── registro_professor.html
│   │   └── dashboard_professor.html
│   ├── groups/
│   │   ├── criar_grupo.html
│   │   ├── detalhe_grupo.html
│   │   ├── area_aluno.html         ← Entrada do aluno via código
│   │   └── sala_estudo.html        ← Sala de estudos do aluno
│   ├── content/
│   │   └── licao_detalhe.html
│   ├── quiz/
│   │   ├── quiz.html               ← Quiz interativo (SPA com JS)
│   │   └── resultado.html
│   └── reports/
│       └── relatorio_grupo.html
│
└── static/
    └── images/
        └── mascote.png             ← Imagem do mascote (Tiger)
```

---

## ⚙️ Setup do Ambiente de Desenvolvimento

### Pré-requisitos

| Ferramenta   | Versão mínima | Como verificar         |
|--------------|--------------|------------------------|
| Python       | 3.11+        | `python --version`     |
| pip          | 23+          | `pip --version`        |
| PostgreSQL   | 15+          | `psql --version`       |
| Git          | qualquer     | `git --version`        |

---

### Passo 1 — Clone o repositório

```bash
git clone https://github.com/seu-usuario/iatica_kids.git
cd iatica_kids
```

---

### Passo 2 — Crie e ative o ambiente virtual

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar no Linux/macOS
source venv/bin/activate

# Ativar no Windows (PowerShell)
venv\Scripts\Activate.ps1

# Ativar no Windows (CMD)
venv\Scripts\activate.bat
```

---

### Passo 3 — Instale as dependências

```bash
pip install -r requirements.txt
```

---

### Passo 4 — Configure o banco de dados PostgreSQL

```bash
# Acesse o PostgreSQL como superusuário
psql -U postgres

# No prompt do psql, execute:
CREATE DATABASE iatica_kids;
CREATE USER iatica_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE iatica_kids TO iatica_user;
\q
```

---

### Passo 5 — Configure as variáveis de ambiente

```bash
# Copie o modelo
cp .env.example .env

# Edite o arquivo .env com seus dados
nano .env   # ou use o editor de sua preferência
```

Conteúdo do `.env`:
```env
SECRET_KEY=troque-por-uma-chave-longa-e-aleatoria
DEBUG=True

DB_NAME=iatica_kids
DB_USER=iatica_user
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

> 💡 Para gerar uma SECRET_KEY segura:
> ```python
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

### Passo 6 — Execute as migrações

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### Passo 7 — Popule o banco com conteúdo inicial

```bash
# Cria as 5 lições e o banco de 8 perguntas do quiz
python manage.py seed_data
```

---

### Passo 8 — Crie um superusuário administrador

```bash
python manage.py createsuperuser
```

---

### Passo 9 — Colete os arquivos estáticos

```bash
python manage.py collectstatic --noinput
```

---

### Passo 10 — Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse: **http://localhost:8000**

---

## 🗺️ URLs Principais

| URL                             | Descrição                              | Acesso          |
|---------------------------------|----------------------------------------|-----------------|
| `/`                             | Página inicial                         | Público         |
| `/contas/registrar/`            | Cadastro de professor                  | Público         |
| `/contas/login/`                | Login                                  | Público         |
| `/dashboard/`                   | Dashboard do professor                 | Professor        |
| `/dashboard/criar-grupo/`       | Criar grupo de estudos                 | Professor        |
| `/dashboard/grupo/<id>/`        | Detalhe do grupo                       | Professor        |
| `/dashboard/alunos/`            | Área do aluno (entrada via código)     | Público         |
| `/dashboard/alunos/sala/<id>/`  | Sala de estudos                        | Aluno (sessão)  |
| `/conteudo/grupo/<g>/licao/<l>/`| Leitura de lição                       | Aluno (sessão)  |
| `/quiz/grupo/<id>/iniciar/`     | Iniciar quiz                           | Aluno (sessão)  |
| `/quiz/resultado/<id>/`         | Resultado do quiz                      | Aluno (sessão)  |
| `/relatorios/grupo/<id>/`       | Relatório web                          | Professor        |
| `/relatorios/grupo/<id>/pdf/`   | Download do relatório em PDF           | Professor        |
| `/admin/`                       | Painel administrativo Django           | Superusuário    |

---

## 🔄 Fluxo Completo de Uso

```
[PROFESSOR]                          [ALUNO]
     │                                  │
     ▼                                  │
 Cria conta                             │
     │                                  │
     ▼                                  │
 Cria grupo ──── gera código ──────────►│
     │                                  ▼
     │                          Acessa /alunos/
     │                          Informa nome + código
     │                                  │
     │                                  ▼
     │                          Entra na Sala de Estudos
     │                                  │
     │                                  ▼
     │                          Lê as 5 Lições
     │                          (marca cada uma)
     │                                  │
     │                                  ▼
     │                          Realiza o Quiz (8 perguntas)
     │                                  │
     │                                  ▼
     │                          Vê seu resultado
     │                                  │
     ▼                                  │
 Professor finaliza grupo ◄─────────────┘
     │
     ▼
 Visualiza Relatório Web
     │
     ▼
 Baixa PDF com desempenho da turma
```

---

## 🛠️ Stack Tecnológica

| Camada        | Tecnologia             |
|---------------|------------------------|
| Backend       | Django 5.0             |
| Banco de dados| PostgreSQL 15          |
| ORM           | Django ORM             |
| Autenticação  | Django Auth (custom)   |
| Templates     | Django Templates       |
| PDF           | ReportLab              |
| Static files  | WhiteNoise             |
| Fontes        | Google Fonts (Nunito, Fredoka One) |

---

## 📚 Conteúdo das Lições

1. **🤖 O que é Inteligência Artificial?** — Como os computadores aprendem
2. **✅ Usando a IA com Responsabilidade** — Uso ético e honesto
3. **🔍 A IA Mente? Entendendo as Alucinações** — Como checar informações
4. **🔒 Privacidade e Segurança com a IA** — Protegendo dados pessoais
5. **⚖️ Ética e Fairness na IA** — Viés, diversidade e justiça

---

## 🐛 Solução de Problemas Comuns

**Erro: `psycopg2` não instala no macOS**
```bash
brew install libpq
pip install psycopg2-binary
```

**Erro de permissão no PostgreSQL**
```sql
ALTER USER iatica_user CREATEDB;
```

**Tabelas não aparecem após `migrate`**
```bash
python manage.py showmigrations   # verifica o status
python manage.py migrate --run-syncdb
```

**Imagem do mascote não aparece**
- Confirme que `static/images/mascote.png` existe
- Execute `python manage.py collectstatic`

---

*Desenvolvido com ❤️ para professores e alunos da educação básica.*
