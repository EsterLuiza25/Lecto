# 📚 Lecto: Reading. Learning. Growth.

O **Lecto** é uma plataforma robusta de aprendizado de inglês focada em compreensão textual gamificada. O sistema oferece uma experiência personalizada onde o conteúdo se adapta ao nível do usuário, integrando uma economia interna de moedas e customização de avatares.

---

## 🎯 Funcionalidades Principais

* **Matriz de Conteúdo Inteligente:** Sistema que gerencia centenas de textos nivelados dinamicamente.
* **Quiz de Nivelamento Interseccional:** Algoritmo que filtra perguntas cruzando `Nível` vs `Categoria`.
* **Sistema de Avatar:** Customização visual em camadas (Corpo, Cabelo, Roupa) com itens desbloqueáveis.
* **Economia Gamificada:** Ganho de moedas por leitura e acertos em quizzes para uso na loja interna.
* **Segurança e Performance:** Configurações prontas para deploy com suporte a variáveis de ambiente, PostgreSQL, SSL e arquivos estáticos via WhiteNoise.

---

## 📊 Estrutura do Catálogo (Big Data Ready)

O Lecto utiliza comandos de *seed* automatizados para gerar uma base de dados massiva, garantindo que o aprendizado seja variado e contínuo. Atualmente, o catálogo conta com:

* **7 Níveis de Proficiência** (do Iniciante ao C2).
* **12 Categorias Temáticas** distintas.
* **840 textos publicados** (10 textos por categoria em cada nível).
* **4.200 perguntas de quiz dos textos** (5 perguntas exclusivas por texto).
* **637 perguntas de nivelamento** filtradas por nível e categoria.
* **Vocabulário destacado por texto**, gerado automaticamente conforme o conteúdo.

O comando `seed_category_placement_quizzes` cria a lógica de nivelamento por interseção, enquanto o `generate_mass_content --only-avatars` reconstrói os ativos visuais necessários para a personalização do usuário.

---

## 🛠️ Instalação e Execução

### Passo a Passo (Powershell)

Para rodar o projeto localmente, execute os seguintes comandos no seu terminal:

```powershell
# Criar e ativar ambiente virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Instalar dependências e configurar ambiente
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edite o arquivo `.env` com os dados do seu ambiente.

Para usar PostgreSQL local, configure a variável `DATABASE_URL`. Exemplo:

```env
DATABASE_URL=postgres://luiza:sua-senha@localhost:5433/lecto_db
```

No PostgreSQL local usado no desenvolvimento deste projeto, a porta ativa foi `5433`. Se o seu PostgreSQL estiver na porta padrão, use `5432`.

```powershell
# Preparar banco de dados e conteúdo
python manage.py migrate
python manage.py seed_initial_data
python manage.py seed_full_catalog
python manage.py seed_category_placement_quizzes
python manage.py generate_mass_content --only-avatars

# Criar usuário administrativo
python manage.py createsuperuser

# Iniciar servidor
python manage.py runserver 127.0.0.1:8000
```

Depois acesse:

```text
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/
```

Se a porta `8000` ficar presa por algum processo antigo, use outra porta:

```powershell
python manage.py runserver 127.0.0.1:8001
```

---

## 🐘 Banco de Dados PostgreSQL

O projeto lê automaticamente o arquivo `.env`. A prioridade de banco é:

1. `DATABASE_URL`, recomendado para Render e produção.
2. Variáveis separadas `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`.
3. SQLite local como fallback, usando `SQLITE_NAME`.

Exemplo com `DATABASE_URL`:

```env
DATABASE_URL=postgresql://usuario:senha@host:5432/banco
```

Exemplo local:

```env
DATABASE_URL=postgres://luiza:sua-senha@localhost:5433/lecto_db
```

Se a senha tiver caracteres especiais, codifique na URL. Exemplos:

```text
@ vira %40
# vira %23
% vira %25
/ vira %2F
: vira %3A
```

Para confirmar qual banco o Django está usando:

```powershell
python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE','lecto.settings'); import django; django.setup(); from django.conf import settings; print(settings.DATABASES['default']['ENGINE']); print(settings.DATABASES['default']['NAME']); print(settings.DATABASES['default'].get('PORT'))"
```

---

## 🚀 Deploy no Render

Antes de subir no Render, suba o código para o GitHub sem incluir `.env`, `db.sqlite3`, `media/`, `.venv/`, `staticfiles/`, logs ou caches. Esses arquivos já estão cobertos pelo `.gitignore`.

No Render, crie:

* Um **PostgreSQL Database**.
* Um **Web Service** conectado ao repositório do GitHub.

### Variáveis de Ambiente no Render

Configure no painel do Render:

```env
DJANGO_SECRET_KEY=uma-chave-grande-e-segura
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=seu-servico.onrender.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://seu-servico.onrender.com
DATABASE_URL=cole-a-internal-database-url-do-render
DJANGO_SESSION_COOKIE_SECURE=1
DJANGO_CSRF_COOKIE_SECURE=1
DJANGO_SECURE_SSL_REDIRECT=1
DJANGO_SECURE_HSTS_SECONDS=31536000
DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS=1
DJANGO_SECURE_HSTS_PRELOAD=0
```

### Build Command

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

### Start Command

```bash
gunicorn lecto.wsgi:application
```

O repositório também inclui um `Procfile` com esse mesmo comando e um `runtime.txt` fixando Python 3.12.6.

### Primeiro Deploy / Banco Limpo

Depois do primeiro deploy, abra o Shell do Render e rode uma vez:

```bash
python manage.py migrate
python manage.py seed_initial_data
python manage.py seed_full_catalog
python manage.py seed_category_placement_quizzes
python manage.py generate_mass_content --only-avatars
python manage.py createsuperuser
```

O comando `seed_full_catalog` agora usa **10 textos por categoria em cada nível** por padrão. Se você já tiver rodado uma versão antiga que criou 30 textos por interseção, limpe com:

```bash
python manage.py prune_text_catalog --keep 10 --delete-media
```

---

## ✅ Checklist Para Publicar

```powershell
python manage.py check
python manage.py test accounts progress core reading quiz
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
```

Para uma checagem próxima de produção, use `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` e rode:

```powershell
python manage.py check --deploy
```

---

## 📁 Arquivos Importantes

* `.env.example`: modelo de variáveis de ambiente.
* `.env`: configuração local privada. Não deve ir para o GitHub.
* `requirements.txt`: dependências do Django, PostgreSQL, Gunicorn e WhiteNoise.
* `Procfile`: comando de inicialização com Gunicorn.
* `runtime.txt`: versão do Python usada no deploy.
* `reading/management/commands/seed_full_catalog.py`: gera o catálogo com 10 textos por categoria em cada nível.
* `quiz/management/commands/seed_category_placement_quizzes.py`: gera perguntas de nivelamento por nível e categoria.

---

## 📚 Documentação

* `docs/PRD.md`
* `docs/BACKLOG.md`
