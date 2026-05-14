# PRD - Lecto

Atualizado em: 2026-05-14

## 1. Visao Geral

O Lecto e um site em portugues para leitores brasileiros que querem praticar leitura em ingles com textos curtos, agradaveis e organizados por nivel de proficiencia.

A plataforma oferece uma biblioteca progressiva de textos em ingles, filtros por nivel e categoria, vocabulario destacado, quizzes de compreensao, explicacao de trechos, perfil de usuario, favoritos, progresso, moedinhas, avatar modular e uma camada inicial de API REST.

O produto deve ser simples de usar, visualmente acolhedor e conectado a identidade do mascote Alexandrinho: um livro-personagem academico, simpatico e voltado para progresso de leitura.

## 2. Objetivo do Produto

Criar uma experiencia de leitura guiada para estudantes brasileiros, ajudando o usuario a:

- Descobrir seu nivel aproximado de leitura.
- Ler textos compativeis com sua proficiencia.
- Evoluir gradualmente entre os niveis.
- Aprender vocabulario novo com traducao, pronuncia escrita e exemplos.
- Pedir explicacao de trechos selecionados na pagina de leitura.
- Explorar temas de interesse como anime, HQs, games, tecnologia, cultura pop e cotidiano.
- Criar conta, personalizar avatar e acompanhar progresso.
- Ganhar moedinhas ao ler textos e responder quizzes.
- Favoritar textos para reler depois.

## 3. Publico-Alvo

- Estudantes brasileiros iniciantes ou intermediarios em ingles.
- Pessoas que querem criar habito de leitura em ingles sem textos longos demais.
- Fas de cultura pop, anime, HQs, games, tecnologia, viagens, musica e temas leves.
- Professores ou tutores que desejam indicar leituras graduadas.

## 4. Proposta de Valor

O Lecto entrega textos em ingles com dificuldade controlada, explicacoes em portugues e experiencia visual amigavel. Em vez de jogar o usuario em artigos longos ou conteudos sem nivelamento, o site guia o leitor por textos curtos, progressivos e tematicamente interessantes.

## 5. Escopo Atual do MVP

### 5.1 Niveis de Leitura

O site possui sete niveis:

- Iniciante
- A1
- A2
- B1
- B2
- C1
- C2

Cada nivel deve ter textos distribuidos entre as categorias ativas.

### 5.2 Catalogo Atual

O catalogo atual foi reduzido para um MVP mais controlado:

- 7 niveis.
- 12 categorias ativas.
- 10 textos por categoria em cada nivel.
- 70 textos por categoria.
- 120 textos por nivel.
- 840 textos publicados no total.

Os textos principais sao em ingles. A interface, filtros, descricoes, feedbacks e resumos sao em portugues.

### 5.3 Categorias Ativas

As categorias ativas no MVP sao:

- Anime
- Contos
- Cotidiano
- Cultura pop
- Games
- HQs
- Meio ambiente
- Musica
- Saude e bem-estar
- Series
- Tecnologia
- Viagens

### 5.4 Categorias Removidas do Escopo Atual

As categorias abaixo foram removidas do MVP para reduzir complexidade e manter foco:

- Biografias curtas
- Carreira e estudos
- Materias
- Noticias
- Esportes
- Misterios e curiosidades
- Ciencia
- Historia
- Cinema

Essas categorias nao aparecem no banco, nao possuem paginas ativas e seus comandos de seed especificos foram removidos.

## 6. Diretrizes de Dificuldade dos Textos

Os textos devem crescer em tamanho, vocabulario e complexidade conforme o nivel aumenta. Mesmo nos niveis altos, a leitura deve continuar agradavel.

| Nivel | Tamanho sugerido | Caracteristicas |
| --- | ---: | --- |
| Iniciante | 40 a 80 palavras | Frases muito curtas, vocabulario concreto, presente simples e repeticao util. |
| A1 | 80 a 120 palavras | Rotina, objetos, lugares, verbos basicos e conectores simples. |
| A2 | 120 a 180 palavras | Pequenas narrativas, passado simples, comparacoes simples e mais detalhes. |
| B1 | 180 a 260 palavras | Opinioes simples, causa e consequencia, conectores e vocabulario mais variado. |
| B2 | 260 a 380 palavras | Argumentacao leve, ideias abstratas, frases mais longas e idiomaticas moderadas. |
| C1 | 380 a 550 palavras | Nuance, estilo, opinioes complexas, vocabulario sofisticado e estruturas variadas. |
| C2 | 550 a 750 palavras | Texto refinado, inferencia, ambiguidade leve, registros variados e vocabulario avancado. |

## 7. Categoria Especial: HQs

A categoria HQs permite associar textos a personagens/herois e filtrar a pagina por personagem.

Personagens cadastrados:

- Spider-Man
- Iron Man
- Captain America
- Thor
- Hulk
- Black Panther
- Doctor Strange
- Wolverine
- Deadpool
- Captain Marvel
- Superman
- Batman
- Wonder Woman
- The Flash
- Aquaman
- Green Lantern
- Green Arrow
- Cyborg
- Harley Quinn
- Joker

Diretrizes de produto:

- Textos de HQs devem ser breves, descritivos, originais e adaptados ao nivel.
- O site nao deve reproduzir trechos oficiais.
- O site nao deve usar imagens oficiais sem licenciamento.
- Prompts de imagem para HQs devem evitar nomes protegidos quando forem enviados a geradores externos.
- Imagens de HQs devem usar descricoes genericas e transformativas, como "heroi com armadura tecnologica" em vez de copiar marcas visuais oficiais.

## 8. Experiencia Principal do Usuario

### 8.1 Pagina Inicial

A home deve apresentar:

- Identidade visual do Lecto e do mascote Alexandrinho.
- Chamada principal para leitura por nivel.
- Acesso rapido aos niveis.
- Bloco de categorias populares.
- Textos recomendados ou recentes.
- Teste rapido de nivelamento.
- Acesso a cadastro, login, perfil e avatar.

### 8.2 Teste de Nivelamento

Regras:

- O quiz de nivelamento tem 7 questoes.
- O usuario escolhe qual nivel deseja testar.
- O quiz pode ser segmentado por categoria.
- Cada questao tem alternativas de multipla escolha.
- O resultado exibe acertos, erros, porcentagem, nivel sugerido e mensagem de orientacao.
- Para considerar proficiencia em um nivel, o usuario precisa acertar pelo menos 5 de 7 questoes.

Mensagens sugeridas:

- 5 a 7 acertos: "Voce demonstrou boa leitura para este nivel. Recomendamos comecar pelos textos de {nivel}."
- 3 a 4 acertos: "Voce esta perto, mas talvez aproveite melhor os textos de um nivel anterior. Tente o teste de {nivel_anterior}."
- 0 a 2 acertos: "Este nivel pode estar dificil agora. Recomendamos comecar por {nivel_anterior} e evoluir aos poucos."

### 8.3 Acesso Sem Login

No estado atual do MVP, a leitura esta temporariamente liberada sem login, com acoes locais de marcar como lido e favoritar via frontend. A arquitetura continua preparada para exigir login e persistir progresso no backend.

### 8.4 Conta, Perfil e Avatar

Usuarios cadastrados devem ter perfil com:

- Avatar editavel.
- Nome de exibicao.
- Nivel recomendado atual.
- Moedinhas acumuladas.
- Historico de leitura.
- Textos favoritos.
- Estatisticas de quizzes.
- Medalhas ou conquistas em fase futura.

### 8.5 Avatar Modular

O avatar foi refatorado para sistema modular por camadas.

Camadas atuais:

- `base_body`
- `body_style`
- `hair_style`
- `outfit`
- `eyes`
- `accessories`

Cada `AvatarOption` possui:

- Nome.
- Tipo de camada.
- Asset SVG/PNG.
- Preco em moedas.
- Ordem de sobreposicao.
- Estado ativo/inativo.

O frontend deve sobrepor as camadas via CSS, permitindo personalizacao visual e gamificacao por itens gratuitos ou desbloqueaveis.

### 8.6 Explicacao de Trechos

A pagina de leitura possui um bloco de explicacao. O usuario seleciona um trecho do texto em ingles e solicita uma explicacao em portugues.

Regras:

- A funcionalidade consome o endpoint `/api/v1/ai/explain/` via `fetch`.
- Quando houver `OPENAI_API_KEY`, o servico pode usar LLM externo para gerar explicacao.
- Quando nao houver chave de API, o sistema usa fallback local com glossario do texto, mini-dicionario interno e regras simples de gramatica.
- A explicacao deve retornar texto em portugues, palavras-chave e uma nota gramatical quando possivel.
- A funcionalidade deve existir em todos os textos que usam a pagina padrao de leitura.

## 9. Paginas de Nivel e Categoria

### 9.1 Pagina de Nivel

Cada pagina de nivel deve conter:

- Titulo do nivel.
- Descricao em portugues.
- Grade de textos.
- Filtro por categoria.
- Busca por palavra-chave.
- Paginacao.

### 9.2 Pagina de Categoria

Cada pagina de categoria deve conter:

- Titulo da categoria.
- Descricao em portugues.
- Grade de textos.
- Filtro por nivel.
- Paginacao.

Na categoria HQs, a pagina tambem deve conter filtro por personagem.

### 9.3 Card de Texto

Cada card deve exibir:

- Imagem principal (`cover_image`) quando existir.
- Ilustracao/animacao (`animation_asset`) como fallback.
- Titulo em ingles.
- Categoria.
- Nivel.
- Tempo estimado de leitura.
- Numero aproximado de palavras.
- Resumo em portugues.
- Link para leitura.

## 10. Pagina de Leitura

Cada texto deve abrir uma pagina propria com:

- Titulo.
- Nivel.
- Categoria.
- Tempo estimado de leitura.
- Imagem principal ou fallback visual.
- Texto principal em ingles.
- Bloco de explicacao de trecho selecionado.
- Secao de vocabulario destacado.
- Quiz de compreensao com 5 perguntas.
- Acoes de favorito e conclusao de leitura.

## 11. Vocabulario Dinamico

O vocabulario foi refatorado para ser especifico de cada texto.

Regras:

- O sistema processa `content_en` de cada `Text`.
- O pipeline identifica candidatos a vocabulario com foco em substantivos, verbos e adjetivos.
- Palavras muito frequentes sao filtradas por lista interna de alta frequencia.
- Cada texto recebe glossario proprio.
- Cada item deve ter palavra, lema, classe gramatical, traducao, pronuncia simplificada, exemplo e fonte.

Campos relevantes:

- `word_en`
- `lemma_en`
- `part_of_speech`
- `translation_pt`
- `pronunciation_pt`
- `ipa`
- `audio_url`
- `tts_provider`
- `example_en`
- `source`
- `frequency_rank`
- `order`

## 12. Quiz de Compreensao

Cada texto pode ter quiz final com 5 perguntas.

Regras:

- Perguntas de multipla escolha.
- Medem compreensao do texto, nao apenas traducao literal.
- Resultado exibe acertos, erros e porcentagem.
- Moedinhas podem ser concedidas conforme desempenho.
- Tentativas devem ser registradas quando o usuario estiver autenticado.

Pontuacao sugerida:

- 0 a 2 acertos: compreensao baixa; sugerir releitura.
- 3 acertos: compreensao parcial; sugerir revisar vocabulario.
- 4 a 5 acertos: boa compreensao; conceder bonus.

## 13. Imagens e Prompts

Cada texto possui campos para:

- `cover_image`: imagem principal, geralmente gerada externamente ou enviada manualmente.
- `animation_asset`: SVG/ilustracao local gerada como fallback.
- `image_prompt`: prompt tecnico usado para gerar imagem.
- `image_canvas_width`
- `image_canvas_height`

### 13.1 Prioridade Visual

Nas telas do site:

1. Usar `cover_image` quando existir.
2. Usar `animation_asset` como fallback.
3. Usar placeholder textual quando nao houver asset.

### 13.2 Prompt Padrao

Prompt tecnico para historias:

`Digital art, 2D cartoon style, clean lines, high quality, [CENA ESPECIFICA EXTRAIDA DO TEXTO], featuring the book-mascot Alexandrinho, using the palette #1C4259 and #D9B97E, no text, no copyright infringement`

### 13.3 Automacao de Imagens

O projeto possui comando para:

- Percorrer todos os textos.
- Gerar `image_prompt`.
- Opcionalmente chamar API externa de imagem.
- Baixar a imagem.
- Salvar em `media/texts/covers/`.
- Atualizar `cover_image`.

O comando tambem gera manifesto de prompts para assets de avatar modular.

## 14. API REST e Integracao com IA

O Lecto permanece uma aplicacao Django SSR, mas agora possui uma camada adicional de API REST para atender integracoes, automacoes e requisitos de residencia.

### 14.1 API REST v1

Base URL:

`/api/v1/`

Endpoints atuais:

- `GET /api/v1/schema/`
- `GET /api/v1/docs/`
- `GET /api/v1/texts/`
- `GET /api/v1/texts/<slug>/`
- `GET /api/v1/vocabulary/`
- `GET /api/v1/vocabulary/?text=<slug>`
- `GET /api/v1/text-quizzes/`
- `GET /api/v1/text-quizzes/?text=<slug>`
- `POST /api/v1/ai/explain/`

Regras:

- As respostas da API devem ser em JSON.
- A API usa Django REST Framework.
- A documentacao OpenAPI/Swagger e gerada com `drf-spectacular`.
- O app responsavel pela camada REST e `api_v1`.
- Os endpoints publicos atuais sao somente leitura, exceto o endpoint de explicacao.

### 14.2 Servico de IA

O modulo `services/ai_engine.py` centraliza funcoes de IA e fallback local.

Funcoes principais:

- `generate_quiz_from_text(text_content)`: gera 5 perguntas de multipla escolha.
- `analyze_text_difficulty(text_content)`: calcula metricas simples de legibilidade e sugere nivel.
- `explain_selection(selection, context="", glossary=None)`: explica um trecho selecionado em portugues.

Comportamento esperado:

- Se `OPENAI_API_KEY` estiver configurada, o servico pode chamar OpenAI.
- Se nao houver chave, o sistema usa fallback local deterministico.
- O fallback local deve continuar util para demonstracao, testes e deploy gratuito.

### 14.3 Automacao de Conteudo

O comando `automate_content` percorre textos publicados sem quiz e usa o `ai_engine` para criar perguntas automaticamente.

Uso:

- `python manage.py automate_content`
- `python manage.py automate_content --limit 10`
- `python manage.py automate_content --dry-run`
- `python manage.py automate_content --overwrite`

O comando popula:

- `TextQuizQuestion`
- `TextQuizAnswer`

### 14.4 Testes Automatizados

Foram adicionados testes para:

- Endpoints REST retornarem JSON.
- Schema OpenAPI e Swagger UI estarem disponiveis.
- Endpoint de vocabulario filtrar por texto.
- Endpoint de quiz retornar alternativas.
- Fluxo de explicacao funcionar com fallback local.
- Servico de IA gerar quiz sem depender de API externa.
- Comando de automacao criar perguntas com mocks.

## 15. Requisitos Funcionais

### RF01 - Listar Niveis

O sistema deve listar Iniciante, A1, A2, B1, B2, C1 e C2.

### RF02 - Paginas de Nivel

O sistema deve ter uma pagina para cada nivel.

### RF03 - Paginas de Categoria

O sistema deve ter uma pagina para cada categoria ativa.

### RF04 - Filtro por Categoria

O usuario deve conseguir filtrar textos por categoria nas paginas de nivel.

### RF05 - Filtro por Nivel

O usuario deve conseguir filtrar textos por nivel nas paginas de categoria.

### RF06 - Filtro por Personagem em HQs

Na categoria HQs, o usuario deve conseguir filtrar textos por personagem.

### RF07 - Busca de Textos

O usuario deve conseguir buscar textos por titulo, resumo, categoria ou palavra-chave.

### RF08 - Pagina de Texto

O usuario deve conseguir abrir um texto e ler o conteudo completo em ingles.

### RF09 - Vocabulario do Texto

Ao final de cada texto, o sistema deve exibir palavras destacadas com traducao, pronuncia escrita e exemplo.

### RF10 - Quiz de Nivelamento

O sistema deve oferecer quiz de 7 questoes para nivelamento.

### RF11 - Quiz por Texto

Cada texto pode ter quiz de 5 perguntas.

### RF12 - Conta e Login

O sistema deve permitir cadastro, login e logout.

### RF13 - Perfil do Usuario

O sistema deve oferecer perfil com avatar, moedas, historico, favoritos e estatisticas.

### RF14 - Avatar Modular

O usuario deve conseguir personalizar avatar por camadas.

### RF15 - Moedinhas

O sistema deve conceder moedinhas por leitura concluida e desempenho em quizzes.

### RF16 - Favoritos

Usuarios devem conseguir favoritar e desfavoritar textos.

### RF17 - Historico

O sistema deve registrar textos iniciados, textos concluidos e data de leitura.

### RF18 - Administracao de Conteudo

Administradores devem conseguir gerenciar textos, categorias, niveis, vocabulario, quizzes, imagens e personagens.

### RF19 - API REST

O sistema deve expor endpoints JSON para textos, vocabulario e quizzes de texto.

### RF20 - Explicacao de Trechos

O usuario deve conseguir selecionar um trecho de um texto e receber uma explicacao em portugues.

### RF21 - Automacao de Quizzes

Administradores devem conseguir gerar quizzes automaticamente para textos sem perguntas por meio de management command.

## 16. Requisitos Nao Funcionais

- O site deve ser responsivo para desktop, tablet e mobile.
- A interface deve ser em portugues.
- Os textos principais devem ser em ingles.
- As paginas devem carregar rapidamente.
- A leitura deve ter boa legibilidade, contraste e espacamento.
- O projeto deve ser construido em Python com Django.
- O frontend do MVP usa Django Templates, CSS proprio e JavaScript leve.
- A camada REST usa Django REST Framework.
- O banco local inicial e SQLite.
- O banco recomendado para producao e PostgreSQL.
- A pontuacao por moedas deve ser calculada no backend quando usuario estiver autenticado.
- A geracao de imagens via API deve ser opcional e acionada por comando, nao automaticamente a cada request.
- A integracao com LLM deve ser opcional e funcionar com fallback local quando nao houver chave de API.
- Testes automatizados devem cobrir API, IA/fallback e comandos criticos.

## 17. Arquitetura Tecnica

Stack:

- Backend: Python + Django.
- API REST: Django REST Framework.
- Banco local: SQLite.
- Banco recomendado para producao: PostgreSQL.
- Frontend: Django Templates, HTML, CSS e JavaScript leve.
- Admin: Django Admin.

Apps:

- `core`: home, avatar e componentes gerais.
- `reading`: niveis, categorias, textos, vocabulario, personagens e pipeline visual.
- `quiz`: perguntas, alternativas, tentativas e resultados.
- `accounts`: cadastro, login, perfil e avatar modular.
- `progress`: historico, favoritos, moedas e conquistas.
- `media_assets`: espaco para evolucao de recursos visuais.
- `api_v1`: endpoints REST em JSON para textos, vocabulario, quizzes e explicacao.
- `services`: camada de servicos compartilhados, incluindo `ai_engine`.

Management commands relevantes:

- `seed_initial_data`
- `seed_full_catalog`
- `generate_mass_content`
- `generate_ai_visual_assets`
- `import_text_cover`
- `prune_text_catalog`
- `refresh_text_illustrations`
- `automate_content`
- comandos `seed_*_stories` das categorias ativas.

## 18. Modelo de Dados Principal

### Level

- `name`
- `slug`
- `order`
- `description_pt`
- `min_words`
- `max_words`

### Category

- `name`
- `slug`
- `description_pt`
- `is_active`

### Character

- `name`
- `slug`
- `publisher`
- `description_pt`
- `is_active`

### Text

- `title`
- `slug`
- `summary_pt`
- `content_en`
- `level`
- `category`
- `character`
- `cover_image`
- `animation_asset`
- `image_prompt`
- `image_canvas_width`
- `image_canvas_height`
- `word_count`
- `estimated_reading_time`
- `is_premium`
- `view_count`
- `status`
- `published_at`
- `created_at`
- `updated_at`

### VocabularyItem

- `text`
- `word_en`
- `lemma_en`
- `part_of_speech`
- `translation_pt`
- `pronunciation_pt`
- `ipa`
- `audio_url`
- `tts_provider`
- `example_en`
- `source`
- `frequency_rank`
- `order`

### UserAvatar

- `user`
- `base_body`
- `body_style`
- `hair_style`
- `outfit`
- `eyes`
- `accessories`
- `updated_at`

### AvatarOption

- `name`
- `option_type`
- `image_asset`
- `color_value`
- `coin_price`
- `layer_order`
- `is_active`

Demais modelos principais:

- `UserProfile`
- `ReadingProgress`
- `FavoriteText`
- `CoinTransaction`
- `Achievement`
- `UserAchievement`
- `PlacementQuizQuestion`
- `PlacementQuizAnswer`
- `QuizAttempt`
- `TextQuizQuestion`
- `TextQuizAnswer`
- `TextQuizAttempt`

## 19. Identidade Visual

Mascote:

- Nome: Alexandrinho.
- Conceito: livro academico simpatico, com tom de guia de leitura.

Paleta:

- Azul profundo: `#1C4259`
- Off-white: `#F2F2EB`
- Dourado claro: `#D9B97E`
- Caramelo: `#BF9663`
- Marrom: `#8C613B`

Direcao visual:

- Base clara para leitura confortavel.
- Azul profundo para navegacao e titulos.
- Dourado e caramelo para destaques e progresso.
- Componentes com bordas discretas e raio pequeno.
- Imagens em estilo cartoon 2D, linhas limpas e boa legibilidade.

## 20. Criterios de Aceite do MVP Atual

- A home exibe identidade do Lecto, niveis, categorias e quiz.
- Existem paginas para Iniciante, A1, A2, B1, B2, C1 e C2.
- Existem paginas para as 12 categorias ativas.
- Cada categoria ativa possui 70 textos.
- Cada categoria possui 10 textos por nivel.
- Cada nivel possui 120 textos.
- O catalogo total possui 840 textos publicados.
- O usuario consegue filtrar textos por categoria.
- O usuario consegue filtrar categorias por nivel.
- A categoria HQs permite filtrar por personagem.
- Cada texto exibe conteudo em ingles, resumo em portugues, vocabulario e quiz.
- Cada texto permite solicitar explicacao de um trecho selecionado.
- Cada texto possui prompt de imagem.
- Cada texto possui asset visual local.
- Cards e paginas de leitura usam `cover_image` quando existir e `animation_asset` como fallback.
- O usuario consegue favoritar e marcar leitura.
- O perfil mostra avatar, moedas, favoritos e historico.
- O avatar modular permite camadas e itens com preco em moedas.
- O site funciona bem em mobile e desktop.
- O conteudo pode ser gerenciado pelo Django Admin.
- A API REST retorna JSON para textos, vocabulario e quizzes.
- A documentacao Swagger/OpenAPI esta disponivel em `/api/v1/docs/` e `/api/v1/schema/`.
- O fallback local de explicacao funciona mesmo sem chave externa de IA.

## 21. Roadmap

### Fase 1 - Fundacao

- Projeto Django.
- Apps principais.
- Modelos principais.
- Django Admin.
- Layout base.
- Home, paginas de nivel, categoria e leitura.

Status: implementado.

### Fase 2 - Conteudo MVP

- 12 categorias ativas.
- 840 textos publicados.
- 10 textos por categoria/nivel.
- Vocabulario dinamico por texto.
- Quizzes por texto.
- Prompts e assets visuais.

Status: implementado, com revisao editorial continua.

### Fase 3 - Conta, Progresso e Avatar

- Cadastro/login.
- Perfil.
- Favoritos.
- Historico.
- Moedinhas.
- Avatar modular por camadas.

Status: parcialmente implementado; precisa endurecer persistencia de acoes sem login.

### Fase 4 - Imagens

- Prompts tecnicos para todos os textos.
- Importacao manual de capas geradas externamente.
- Integracao opcional com API de imagem.
- Priorizacao de `cover_image` nas telas.

Status: pipeline implementado; geracao massiva depende de provedor externo/custos.

### Fase 5 - Polimento

- Revisar textos.
- Revisar vocabulario.
- Melhorar acessibilidade.
- Melhorar SEO.
- Integrar audio/pronuncia sintetizada.
- Preparar deploy.

Status: pendente/em andamento.

### Fase 6 - API, IA e Automacao

- Criar API REST v1.
- Documentar API com OpenAPI/Swagger.
- Expor textos, vocabulario e quizzes em JSON.
- Criar servico `ai_engine`.
- Criar explicacao de trecho por endpoint.
- Criar fallback local sem chave de API.
- Criar comando `automate_content`.
- Criar testes com mocks para IA e automacao.

Status: implementado como base inicial; pendente endurecimento de seguranca, limites de uso, cache e revisao editorial automatizada.

## 22. Metricas de Sucesso

- Numero de textos lidos por usuario.
- Taxa de conclusao do quiz.
- Categorias mais acessadas.
- Niveis mais acessados.
- Tempo medio na pagina de leitura.
- Cliques em palavras de vocabulario.
- Uso do recurso de explicacao de trechos.
- Chamadas aos endpoints da API.
- Quizzes gerados por automacao.
- Quizzes de texto concluidos.
- Media de acertos nos quizzes.
- Textos favoritados.
- Moedinhas geradas por usuario.
- Avatares editados.
- Retorno de usuarios para novos textos.

## 23. Decisoes de Produto Confirmadas

1. A home e o quiz inicial podem ser acessados sem login.
2. A leitura esta temporariamente aberta no MVP, mas a arquitetura permite exigir login depois.
3. O usuario pode trocar manualmente de nivel mesmo apos recomendacao.
4. Os textos podem ser criados manualmente e com apoio de IA, com revisao humana.
5. O quiz de nivelamento e separado por nivel e pode considerar categoria.
6. O nome "Iniciante" permanece antes do A1.
7. O tom do site deve equilibrar academico e divertido.
8. HQs devem usar textos originais e imagens transformativas, evitando copia direta.
9. O mascote se chama Alexandrinho.
10. O MVP atual prioriza experiencia completa e catalogo enxuto, nao quantidade maxima.
11. O projeto permanece SSR, mas passa a oferecer API REST v1 paralela.
12. Recursos de IA devem funcionar com fallback local quando nao houver chave externa.
13. Automacoes via management command devem ser opt-in, nunca executadas automaticamente a cada request.
