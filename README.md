# 📚 Lecto: Reading. Learning. Growth.

O **Lecto** é uma plataforma robusta de aprendizado de inglês focada em compreensão textual gamificada. O sistema oferece uma experiência personalizada onde o conteúdo se adapta ao nível do usuário, integrando uma economia interna de moedas e customização de avatares.

---

## 🎯 Funcionalidades Principais

* **Matriz de Conteúdo Inteligente:** Sistema que gerencia centenas de textos nivelados dinamicamente.
* **Quiz de Nivelamento Interseccional:** Algoritmo que filtra perguntas cruzando `Nível` vs `Categoria`.
* **Sistema de Avatar:** Customização visual em camadas (Corpo, Cabelo, Roupa) com itens desbloqueáveis.
* **Economia Gamificada:** Ganho de moedas por leitura e acertos em quizzes para uso na loja interna.
* **Segurança e Performance:** Configurações prontas para deploy com suporte a variáveis de ambiente e SSL.

---

## 📊 Estrutura do Catálogo (Big Data Ready)

O Lecto utiliza comandos de *seed* automatizados para gerar uma base de dados massiva, garantindo que o aprendizado seja variado e contínuo. Atualmente, o catálogo conta com:

* **7 Níveis de Proficiência** (do Iniciante ao C2).
* **12 Categorias Temáticas** distintas.
* **840 textos publicados** (10 textos por categoria em cada nível).
* **4.200 palavras de vocabulário** (5 termos destacados por texto).
* **4.200 perguntas de quiz** (5 perguntas exclusivas por texto).

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

# Preparar banco de dados e conteúdo
python manage.py migrate
python manage.py seed_initial_data
python manage.py seed_full_catalog
python manage.py seed_category_placement_quizzes
python manage.py generate_mass_content --only-avatars

# Iniciar servidor
python manage.py runserver 127.0.0.1:8000
