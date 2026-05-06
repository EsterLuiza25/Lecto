## 📚 Lecto: Reading. Learning. Growth.
O Lecto é uma plataforma robusta de aprendizado de inglês focada em compreensão textual gamificada. O sistema oferece uma experiência personalizada onde o conteúdo se adapta ao nível do usuário, integrando uma economia interna de moedas e customização de avatares.
---
## 🎯 Funcionalidades Principais
Matriz de Conteúdo Inteligente: Sistema que gerencia centenas de textos nivelados dinamicamente.

Quiz de Nivelamento Interseccional: Algoritmo que filtra perguntas cruzando Nível vs Categoria.

Sistema de Avatar: Customização visual em camadas (Corpo, Cabelo, Roupa) com itens desbloqueáveis.

Economia Gamificada: Ganho de moedas por leitura e acertos em quizzes para uso na loja interna.

Segurança e Performance: Configurações prontas para deploy com suporte a variáveis de ambiente e SSL.

---
## 📊 Estrutura do Catálogo (Big Data Ready)
O Lecto utiliza comandos de seed automatizados para gerar uma base de dados massiva, garantindo que o aprendizado seja variado e contínuo. Atualmente, o catálogo conta com:

7 Níveis de Proficiência (do Iniciante ao C2).

12 Categorias Temáticas distintas.

840 textos publicados (10 textos por categoria em cada nível).

4.200 palavras de vocabulário (5 termos destacados por texto).

4.200 perguntas de quiz (5 perguntas exclusivas por texto).

O comando seed_category_placement_quizzes cria a lógica de nivelamento por interseção, enquanto o generate_mass_content --only-avatars reconstrói os ativos visuais necessários para a personalização do usuário.

## 🛠️ Instalação e Execução
Passo a Passo (Powershell)
Para rodar o projeto localmente, siga os comandos abaixo no seu terminal:

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

Após a execução, acesse http://127.0.0.1:8000/. Você também pode utilizar o inicializador simplificado .\abrir-lecto.bat ou a task do VS Code Rodar Lecto.

## 🔒 Configurações e Segurança
O projeto utiliza variáveis de ambiente para gerenciar dados sensíveis. Utilize o arquivo .env.example como referência para configurar sua DJANGO_SECRET_KEY, o modo DJANGO_DEBUG e as definições de segurança para produção HTTPS. O campo OPENAI_API_KEY é opcional e utilizado apenas para comandos de geração de imagens por IA.

## 🏗️ Checklist de Qualidade
Antes de publicar ou realizar novos commits, certifique-se de validar a integridade do código:

python manage.py check --deploy
python manage.py test accounts progress core reading quiz
python manage.py collectstatic --noinput

📄 Documentação
Para mais detalhes sobre o planejamento e a arquitetura do projeto, consulte os arquivos em docs/PRD.md e docs/BACKLOG.md.
