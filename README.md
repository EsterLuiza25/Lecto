# Lecto

Lecto e uma plataforma Django para leitura em ingles por nivel, com interface em portugues, quiz de nivelamento, perfil de usuario, favoritos, avatar e sistema de moedinhas.

## Como rodar localmente

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py seed_initial_data
python manage.py seed_full_catalog
python manage.py seed_category_placement_quizzes
python manage.py generate_mass_content --only-avatars
python manage.py runserver 127.0.0.1:8000
```

Depois acesse `http://127.0.0.1:8000/`.

Com esse comando o Django recarrega automaticamente quando arquivos Python, templates, CSS ou JS forem alterados.

Ou use o inicializador simples:

```powershell
.\abrir-lecto.bat
```

Ele roda o mesmo servidor Django em `http://127.0.0.1:8000/` e mostra qualquer erro diretamente na janela.

Importante: mantenha a janela do inicializador aberta enquanto estiver usando o site.

No VS Code tambem existe a task `Rodar Lecto`, que executa o servidor no terminal integrado.

## Conteudo inicial

O comando `seed_full_catalog` gera a matriz completa do catalogo:

- 7 niveis.
- 12 categorias.
- 10 textos por categoria em cada nivel.
- 840 textos publicados.
- 5 palavras de vocabulario por texto.
- 5 perguntas de quiz por texto.

O comando `seed_category_placement_quizzes` cria perguntas de nivelamento por intersecao de nivel e categoria. O comando `generate_mass_content --only-avatars` recria os SVGs dos itens do avatar dentro de `media/`, que nao vai para o GitHub.

No estado atual, a leitura esta liberada sem login para facilitar a exploracao do site.

## Configuracao

Use `.env.example` como referencia para variaveis de ambiente:

- `DJANGO_SECRET_KEY`: chave secreta do Django. Troque antes de publicar.
- `DJANGO_DEBUG`: use `0` em producao.
- `DJANGO_ALLOWED_HOSTS`: dominios separados por virgula.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: origens HTTPS separadas por virgula, quando necessario.
- `SQLITE_NAME`: caminho do banco SQLite local.
- `DJANGO_SESSION_COOKIE_SECURE`, `DJANGO_CSRF_COOKIE_SECURE`, `DJANGO_SECURE_SSL_REDIRECT`, `DJANGO_SECURE_HSTS_SECONDS`, `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS` e `DJANGO_SECURE_HSTS_PRELOAD`: ajustes de seguranca para producao HTTPS.
- `OPENAI_API_KEY`: opcional, apenas para comandos de geracao de imagens por IA.

Antes de subir para o GitHub, nao inclua `db.sqlite3`, `.env`, `media/`, `.venv/`, logs ou caches. Esses arquivos ja estao cobertos pelo `.gitignore`.

## Checklist para publicar

```powershell
python manage.py check
python manage.py check --deploy
python manage.py test accounts progress core reading quiz
python manage.py makemigrations --check --dry-run
python manage.py collectstatic --noinput
```

Para uma base limpa em producao, rode `migrate` e depois os comandos de seed necessarios no ambiente de destino, em vez de versionar o banco local.

## Documentacao

- `docs/PRD.md`
- `docs/BACKLOG.md`
