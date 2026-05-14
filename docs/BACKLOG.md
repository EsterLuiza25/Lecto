# Backlog - Lecto

Atualizado em: 2026-05-14

## 1. Decisoes Confirmadas

- O MVP atual usa catalogo enxuto: 12 categorias, 7 niveis e 840 textos.
- Cada categoria ativa possui 70 textos.
- Cada categoria possui 10 textos por nivel.
- Cada nivel possui 120 textos.
- Categorias removidas do escopo atual: biografias curtas, carreira e estudos, materias, noticias, esportes, misterios e curiosidades, ciencia, historia e cinema.
- A leitura esta temporariamente aberta sem login.
- A arquitetura continua preparada para exigir login no futuro.
- Cada texto deve ter vocabulario destacado.
- Cada texto pode ter quiz final de 5 perguntas.
- O usuario ganha moedinhas por leitura e desempenho.
- O avatar e modular por camadas.
- O cadastro/perfil deve permitir interesses entre categorias ativas.
- Alexandrinho deve aparecer como guia visual e conceitual.
- O MVP deve priorizar experiencia completa, conteudo revisavel e manutencao simples.
- Imagens geradas por IA devem ser opcionais e podem ser importadas manualmente.
- O projeto continua SSR, mas agora possui API REST v1 paralela.
- Recursos de IA devem funcionar com fallback local quando nao houver chave externa.
- Automacoes de IA devem ser executadas por comando, nao durante requests comuns.

## 2. Status Geral

### Implementado

- Projeto Django.
- Apps principais.
- Modelos de leitura, quiz, progresso, contas e avatar.
- 12 categorias ativas.
- 840 textos publicados.
- Vocabulario dinamico por texto.
- Quizzes por texto.
- Paginas de nivel e categoria.
- Filtro por categoria.
- Filtro por nivel.
- Filtro por personagem em HQs.
- Cards com prioridade para `cover_image` e fallback para `animation_asset`.
- Pipeline de prompts para imagens.
- Comando para importar capa manualmente.
- Comando para podar catalogo.
- Avatar modular com camadas e preco em moedas.
- API REST v1 com endpoints JSON para textos, vocabulario e quizzes.
- Documentacao OpenAPI/Swagger em `/api/v1/schema/` e `/api/v1/docs/`.
- Endpoint `/api/v1/ai/explain/` para explicar trechos selecionados.
- Servico `services/ai_engine.py` com geracao de quiz, analise de dificuldade e explicacao.
- Fallback local de explicacao sem chave de API externa.
- Comando `automate_content` para gerar quizzes automaticamente.
- Testes automatizados para API, IA/fallback e automacao.

### Pendente ou Em Andamento

- Revisao editorial fina dos textos.
- Revisao das traducoes do vocabulario.
- Melhorias de UX no quiz inicial.
- Persistencia completa de favoritos/leitura para visitantes convertidos em usuarios.
- Audio/pronuncia sintetizada.
- Deploy e configuracao de producao.
- Ampliar cobertura de testes automatizados.
- SEO e acessibilidade.
- Rate limit, cache e seguranca para endpoints de IA.

## 3. Epico: Fundacao Django

### Objetivo

Manter a base tecnica do projeto estavel, organizada e pronta para evolucao.

### Tarefas

- [x] Criar projeto Django.
- [x] Criar apps `core`, `accounts`, `reading`, `quiz`, `progress` e `media_assets`.
- [x] Configurar templates globais.
- [x] Configurar arquivos estaticos.
- [x] Configurar SQLite local.
- [x] Configurar Django Admin.
- [x] Criar dados iniciais via management commands.
- [x] Preparar configuracao de producao com PostgreSQL.
- [x] Criar testes basicos de smoke.
- [ ] Criar checklist de deploy.

### Criterios de Aceite

- Projeto roda localmente.
- Admin esta acessivel.
- Home, categorias, niveis e leitura respondem sem erro.
- `manage.py check` nao apresenta erros.

## 4. Epico: Identidade Visual e UI Base

### Objetivo

Criar uma interface acolhedora, legivel e consistente com Alexandrinho.

### Tarefas

- [x] Definir paleta principal.
- [x] Criar CSS base.
- [x] Criar cards de texto.
- [x] Criar filtros.
- [x] Criar paginas principais.
- [x] Adicionar mascote/identidade visual.
- [ ] Revisar contraste com ferramenta de acessibilidade.
- [ ] Refinar estados vazios.
- [ ] Criar pagina 404 personalizada.

### Criterios de Aceite

- Interface funciona em desktop e mobile.
- Textos sao confortaveis de ler.
- Cards nao quebram layout com imagens ou textos longos.

## 5. Epico: Home e Quiz Inicial

### Objetivo

Permitir que visitantes conhecam o Lecto, escolham niveis/categorias e facam nivelamento.

### Tarefas

- [x] Criar pagina inicial.
- [x] Exibir niveis.
- [x] Exibir categorias populares.
- [x] Exibir textos recentes/recomendados.
- [x] Criar bloco de quiz.
- [ ] Revisar UX do quiz em mobile.
- [ ] Melhorar selecao de categoria no quiz.
- [ ] Salvar resultado do quiz para usuario autenticado.
- [ ] Criar chamada de cadastro apos resultado.

### Criterios de Aceite

- Visitante consegue iniciar quiz.
- Resultado exibe acertos, erros, porcentagem e recomendacao.
- Usuario consegue navegar por outros niveis mesmo apos recomendacao.

## 6. Epico: Cadastro, Login e Perfil

### Objetivo

Permitir que usuarios tenham conta, avatar, progresso e favoritos persistentes.

### Tarefas

- [x] Implementar modelos de perfil.
- [x] Implementar login/logout/cadastro basico.
- [x] Criar pagina de perfil.
- [x] Exibir saldo de moedas.
- [x] Exibir favoritos.
- [x] Exibir historico.
- [ ] Refinar cadastro.
- [ ] Permitir editar interesses no perfil.
- [ ] Migrar acoes locais de visitante para conta ao fazer login.

### Criterios de Aceite

- Usuario consegue criar conta.
- Usuario consegue entrar e sair.
- Perfil mostra avatar, moedas, historico e favoritos.

## 7. Epico: Avatar Modular

### Objetivo

Dar identidade visual ao usuario e conectar personalizacao com gamificacao.

### Tarefas

- [x] Criar modelo `AvatarOption`.
- [x] Criar modelo `UserAvatar`.
- [x] Refatorar avatar para camadas.
- [x] Adicionar `base_body`.
- [x] Adicionar `body_style`.
- [x] Adicionar `hair_style`.
- [x] Adicionar `outfit`.
- [x] Adicionar `eyes`.
- [x] Adicionar `accessories`.
- [x] Adicionar preco em moedas.
- [x] Criar assets SVG locais.
- [x] Criar manifesto de prompts para assets gerados por IA.
- [ ] Melhorar polimento visual das camadas.
- [ ] Criar mais opcoes gratuitas.
- [ ] Criar loja visual de itens bloqueados/desbloqueados.

### Criterios de Aceite

- Usuario consegue montar avatar por camadas.
- Camadas sobrepoem corretamente.
- Itens gratuitos podem ser escolhidos sem moedas.
- Itens pagos respeitam saldo de moedas.

## 8. Epico: Catalogo de Leitura

### Objetivo

Organizar textos por nivel, categoria e interesse.

### Tarefas

- [x] Criar modelo `Level`.
- [x] Criar modelo `Category`.
- [x] Criar modelo `Character`.
- [x] Criar modelo `Text`.
- [x] Cadastrar 7 niveis.
- [x] Cadastrar 12 categorias ativas.
- [x] Cadastrar 20 personagens de HQs.
- [x] Criar paginas por nivel.
- [x] Criar paginas por categoria.
- [x] Criar cards de texto.
- [x] Criar filtro por categoria.
- [x] Criar filtro por nivel.
- [x] Criar filtro por personagem em HQs.
- [x] Reduzir catalogo para 10 textos por categoria/nivel.
- [ ] Melhorar busca por titulo, resumo e conteudo.
- [ ] Criar ordenacao por mais recentes, mais lidos, mais curtos e mais longos.

### Criterios de Aceite

- Cada nivel possui pagina propria.
- Cada categoria ativa possui pagina propria.
- Cada categoria possui 70 textos.
- Cada nivel possui 120 textos.
- Usuario consegue filtrar textos.
- HQs permite filtro por personagem.

## 9. Epico: Pagina de Leitura

### Objetivo

Criar experiencia clara, progressiva e recompensadora.

### Tarefas

- [x] Criar pagina de detalhe do texto.
- [x] Exibir titulo, nivel, categoria e tempo de leitura.
- [x] Exibir imagem principal ou fallback.
- [x] Exibir conteudo em ingles.
- [x] Exibir vocabulario.
- [x] Exibir botao de quiz.
- [x] Adicionar explicacao de trecho selecionado.
- [x] Permitir favoritar.
- [x] Permitir marcar como lido.
- [x] Exigir quiz do texto antes de liberar recompensa de leitura.
- [ ] Definir regra final de login obrigatorio ou leitura aberta.
- [ ] Melhorar mensagem de conclusao com Alexandrinho.

### Criterios de Aceite

- Texto abre sem erro.
- Imagem principal aparece quando `cover_image` existe.
- Fallback aparece quando nao existe capa.
- Leitura concluida pode gerar progresso.

## 10. Epico: Vocabulario e Pronuncia

### Objetivo

Ajudar o usuario a aprender palavras importantes de cada texto.

### Tarefas

- [x] Criar modelo `VocabularyItem`.
- [x] Adicionar `lemma_en`.
- [x] Adicionar `part_of_speech`.
- [x] Adicionar `source`.
- [x] Adicionar `frequency_rank`.
- [x] Criar pipeline de vocabulario dinamico.
- [x] Substituir vocabulario fixo por vocabulario por texto.
- [ ] Revisar traducoes pendentes.
- [ ] Adicionar IPA quando disponivel.
- [ ] Integrar audio/pronuncia sintetizada.

### Criterios de Aceite

- Cada texto mostra vocabulario ao final.
- Cada palavra tem traducao ou marcador de traducao pendente.
- Cada palavra tem pronuncia escrita.
- Cada palavra tem exemplo em ingles.

## 11. Epico: Quiz de Compreensao por Texto

### Objetivo

Medir entendimento do texto e recompensar desempenho.

### Tarefas

- [x] Criar modelo `TextQuizQuestion`.
- [x] Criar modelo `TextQuizAnswer`.
- [x] Criar modelo `TextQuizAttempt`.
- [x] Permitir 5 perguntas por texto.
- [x] Exibir quiz ao final da leitura.
- [x] Calcular acertos, erros e porcentagem.
- [x] Mostrar feedback por desempenho.
- [x] Mostrar quais perguntas o usuario acertou e errou.
- [x] Bloquear repeticao do formulario apos resultado.
- [ ] Revisar qualidade das perguntas.
- [ ] Evitar recompensa cheia repetida em tentativas repetidas.

### Criterios de Aceite

- Cada texto pode ter 5 perguntas.
- Resultado e exibido imediatamente.
- Moedinhas sao calculadas no backend para usuario autenticado.
- Tentativa fica registrada no perfil.

## 12. Epico: Moedinhas, XP e Gamificacao

### Objetivo

Criar motivacao leve e saudavel para leitura recorrente.

### Tarefas

- [x] Criar modelo `CoinTransaction`.
- [x] Criar saldo de moedas no perfil.
- [x] Conceder moedas por leitura concluida.
- [x] Preparar compra/desbloqueio de avatar.
- [ ] Conceder +1 moeda por resposta correta.
- [ ] Conceder bonus por 4 ou 5 acertos.
- [ ] Definir recompensa reduzida para releituras.
- [ ] Criar medalhas iniciais.
- [ ] Exibir medalhas no perfil.

### Criterios de Aceite

- Moedas aparecem no perfil.
- Transacoes ficam registradas.
- Usuario entende por que ganhou ou gastou moedas.

## 13. Epico: Favoritos e Historico

### Objetivo

Permitir que usuarios salvem textos e acompanhem leitura.

### Tarefas

- [x] Criar modelo `FavoriteText`.
- [x] Criar modelo `ReadingProgress`.
- [x] Criar botao de favoritar.
- [x] Criar lista de favoritos no perfil.
- [x] Criar historico no perfil.
- [ ] Melhorar sincronizacao entre visitante e usuario autenticado.
- [ ] Permitir remover favorito em lote.

### Criterios de Aceite

- Usuario favorita e remove favorito.
- Favoritos aparecem no perfil.
- Historico mostra textos lidos.

## 14. Epico: Imagens e Assets Visuais

### Objetivo

Usar recursos visuais para aumentar interesse e representar o conteudo do texto.

### Tarefas

- [x] Adicionar `cover_image`.
- [x] Adicionar `animation_asset`.
- [x] Adicionar `image_prompt`.
- [x] Adicionar canvas 500x500.
- [x] Criar gerador local de SVG fallback.
- [x] Criar pipeline de prompts tecnicos.
- [x] Criar comando para importar capa local.
- [x] Priorizar `cover_image` nos cards e paginas.
- [x] Criar diretriz para HQs sem copia direta.
- [ ] Gerar/importar capas reais para textos prioritarios.
- [ ] Criar fila de revisao visual.
- [ ] Compactar imagens grandes.

### Criterios de Aceite

- Cards exibem imagem ou fallback.
- Pagina de leitura exibe imagem ou fallback.
- Prompts ficam salvos no banco.
- HQs usam descricao transformativa, sem logos oficiais.

## 15. Epico: Conteudo MVP

### Objetivo

Manter catalogo menor, revisavel e coerente.

### Tarefas

- [x] Gerar lotes de textos por categoria.
- [x] Podar catalogo para 10 textos por categoria/nivel.
- [x] Remover categorias fora de escopo.
- [x] Remover comandos seed das categorias removidas.
- [x] Validar contagem final de 840 textos.
- [ ] Revisar amostras por categoria e nivel.
- [ ] Corrigir frases estranhas encontradas.
- [ ] Melhorar resumos em portugues.
- [ ] Revisar vocabulario com traducoes confiaveis.

### Criterios de Aceite

- Catalogo total tem 840 textos.
- Cada categoria tem 70 textos.
- Cada categoria tem 10 textos por nivel.
- Cada texto respeita faixa de palavras do nivel.

## 16. Epico: Admin e Curadoria

### Objetivo

Permitir gerenciamento de conteudo pelo Django Admin.

### Tarefas

- [x] Configurar admin de niveis.
- [x] Configurar admin de categorias.
- [x] Configurar admin de textos.
- [x] Configurar admin de vocabulario.
- [x] Configurar admin de personagens.
- [ ] Melhorar filtros no admin.
- [ ] Melhorar busca no admin.
- [ ] Adicionar acoes em lote.
- [ ] Criar dashboard simples de qualidade de conteudo.

### Criterios de Aceite

- Admin consegue criar e editar textos.
- Admin consegue publicar e arquivar conteudo.
- Admin consegue associar vocabulario e imagens aos textos.

## 17. Epico: API REST v1

### Objetivo

Expor dados essenciais do Lecto em JSON para atender integracoes, automacoes e requisitos de API REST.

### Tarefas

- [x] Adicionar `django-rest-framework`.
- [x] Criar app `api_v1`.
- [x] Criar serializers para `Text`, `VocabularyItem`, `TextQuizQuestion` e `TextQuizAnswer`.
- [x] Criar endpoint `GET /api/v1/texts/`.
- [x] Criar endpoint `GET /api/v1/texts/<slug>/`.
- [x] Criar endpoint `GET /api/v1/vocabulary/`.
- [x] Criar endpoint `GET /api/v1/text-quizzes/`.
- [x] Criar endpoint `POST /api/v1/ai/explain/`.
- [x] Configurar respostas como JSON.
- [x] Criar testes de API.
- [x] Adicionar documentacao OpenAPI/Swagger.
- [ ] Adicionar paginacao explicita na API.
- [ ] Definir autenticacao para endpoints sensiveis futuros.

### Criterios de Aceite

- Endpoints retornam JSON.
- Textos publicados podem ser listados via API.
- Vocabulario pode ser filtrado por texto.
- Quizzes podem ser filtrados por texto.
- Testes automatizados cobrem os endpoints principais.
- Documentacao Swagger abre em `/api/v1/docs/`.

## 18. Epico: IA e Explicacao de Trechos

### Objetivo

Permitir apoio inteligente na leitura e manter o recurso funcional mesmo sem chave externa de IA.

### Tarefas

- [x] Criar modulo `services/ai_engine.py`.
- [x] Criar `generate_quiz_from_text`.
- [x] Criar `analyze_text_difficulty`.
- [x] Criar `explain_selection`.
- [x] Integrar opcionalmente com OpenAI via `OPENAI_API_KEY`.
- [x] Criar fallback local para explicacao sem chave de API.
- [x] Usar glossario do texto no fallback local.
- [x] Adicionar bloco de explicacao na pagina de leitura.
- [x] Consumir `/api/v1/ai/explain/` com `fetch`.
- [x] Criar testes com mocks/fallback.
- [ ] Melhorar mini-dicionario local.
- [ ] Adicionar cache por trecho explicado.
- [ ] Adicionar limite de uso por usuario/IP.
- [ ] Melhorar formatacao da explicacao no frontend.

### Criterios de Aceite

- Usuario seleciona trecho e recebe explicacao em portugues.
- O recurso funciona sem `OPENAI_API_KEY`.
- Quando houver chave, o servico pode usar LLM externo.
- Testes nao dependem de chamadas externas.

## 19. Epico: Automacao de Conteudo

### Objetivo

Reduzir trabalho manual de curadoria usando comandos controlados de automacao.

### Tarefas

- [x] Criar comando `automate_content`.
- [x] Percorrer textos publicados sem quiz.
- [x] Gerar perguntas via `ai_engine`.
- [x] Criar `TextQuizQuestion` e `TextQuizAnswer`.
- [x] Adicionar `--limit`.
- [x] Adicionar `--dry-run`.
- [x] Adicionar `--overwrite`.
- [x] Criar teste com mock para fluxo de automacao.
- [ ] Adicionar relatorio CSV/JSON das perguntas geradas.
- [ ] Adicionar fila de revisao editorial antes de publicar perguntas.
- [ ] Adicionar marcacao de origem IA/manual nas perguntas.

### Criterios de Aceite

- Comando gera quizzes sem quebrar textos existentes.
- `--dry-run` simula sem gravar no banco.
- Teste automatizado garante o fluxo principal.

## 20. Epico: Recomendacoes por Interesse

### Objetivo

Usar interesses do usuario para sugerir textos relevantes.

### Tarefas

- [x] Modelo permite interesses por categoria.
- [ ] Filtrar interesses somente entre categorias ativas.
- [ ] Permitir editar interesses no perfil.
- [ ] Recomendar textos por categoria favorita.
- [ ] Recomendar textos por nivel atual.
- [ ] Exibir recomendacoes na home logada.

### Criterios de Aceite

- Usuario escolhe interesses.
- Recomendacoes consideram interesses e nivel.
- Usuario pode editar interesses.

## 21. Epico: Qualidade, Responsividade e Acessibilidade

### Objetivo

Garantir experiencia estavel, legivel e agradavel.

### Tarefas

- [x] Layout responsivo principal.
- [x] Cards responsivos.
- [x] Avatar responsivo.
- [ ] Testar desktop.
- [ ] Testar tablet.
- [ ] Testar mobile.
- [ ] Validar contraste.
- [ ] Validar navegacao por teclado.
- [ ] Revisar formularios.
- [ ] Criar paginas 404 e 500.

### Criterios de Aceite

- Site funciona bem em telas pequenas.
- Leitura e confortavel.
- Formularios sao compreensiveis.
- Estados vazios orientam o usuario.

## 22. Epico: Performance e Deploy

### Objetivo

Preparar o Lecto para ambiente de producao.

### Tarefas

- [ ] Configurar variaveis de ambiente.
- [ ] Separar settings de desenvolvimento e producao.
- [ ] Configurar banco PostgreSQL.
- [ ] Configurar armazenamento de media.
- [ ] Configurar coleta de static files.
- [ ] Revisar seguranca de `SECRET_KEY`, `DEBUG` e `ALLOWED_HOSTS`.
- [ ] Criar comandos de backup do banco.
- [ ] Documentar deploy.

### Criterios de Aceite

- Aplicacao sobe em ambiente externo.
- Midias e estaticos carregam corretamente.
- Dados sensiveis nao ficam hardcoded.

## 23. Fases Futuras

- Audio completo dos textos gerado por IA.
- Teste adaptativo completo.
- Comentarios de usuarios.
- Aplicativo mobile.
- Planos premium.
- Ranking opcional entre amigos.
- Trilhas de leitura por objetivo.
- Certificados de conclusao por nivel.
- Reintroduzir categorias removidas apenas se houver necessidade editorial clara.
