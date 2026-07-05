# Analisador Preditivo de Bancas

## O que é este projeto

Produto de software que aplica ciência de dados a provas anteriores de concursos públicos
brasileiros para prever quais tópicos têm maior probabilidade de serem cobrados e gerar
planos de estudo priorizados.

**Tese central**: cursos preparatórios tratam o edital como lista plana. Na prática, cada
banca tem perfil estatístico próprio dentro de cada disciplina (a distribuição de questões
entre tópicos varia por banca e por cargo). Estudar orientado por esses dados otimiza anos
de preparação. Ninguém no mercado brasileiro faz isso com rigor estatístico.

## Sobre o usuário

Físico com doutorado, professor universitário. Domina Python, estatística e modelagem
preditiva. **NÃO é da área jurídica** — quando a classificação de tópicos exigir juízo
jurídico fino, sinalizar explicitamente e concentrar no fluxo de revisão manual, nunca
assumir.

## Restrição fundamental: custo zero de operação (2026-07-04)

O projeto NÃO pode depender de API paga, serviço em nuvem com cobrança ou modelo
de linguagem remoto. Tudo roda localmente com bibliotecas de código aberto.
Classificação de tópicos: NLP clássico (regras, TF-IDF, scikit-learn) e, só se
necessário, embeddings locais com sentence-transformers em CPU. Se alguma etapa
ficaria melhor com serviço pago, implementar a alternativa gratuita e registrar
a sugestão aqui — nunca deixar a arquitetura dependente do serviço pago.
Hospedagem futura em camadas gratuitas (GitHub Pages, Streamlit Community
Cloud, Hugging Face Spaces).

**Sugestões registradas para avaliação futura (não implementar sem novo aval):**
- Classificação via API da Anthropic com JSON estruturado: chegou a ser
  implementada (histórico do git, commit 9d838ea, `src/classificacao/llm.py`)
  mas foi REMOVIDA sem nunca ser executada, quando o custo zero virou requisito.
  Se um dia houver orçamento, é o melhor candidato a terceira camada.

## Escopo do MVP (recorte deliberado)

- **Carreira piloto**: PF (Agente) e PRF (Policial Rodoviário Federal), nível superior.
- **Disciplinas piloto**: Direito Constitucional, Direito Administrativo, Direito Penal.
- **Banca piloto**: CEBRASPE (formato certo/errado). FGV e FCC entram na Fase 6, mas o
  schema do banco já nasce preparado para múltiplas bancas e múltipla escolha.
- **Fonte de dados**: EXCLUSIVAMENTE provas e gabaritos publicados oficialmente pelas
  bancas em seus sites. NUNCA fazer scraping de plataformas privadas (Qconcursos,
  TEC Concursos etc.). Se houver limitação de acesso, avisar o usuário antes de contornar.
- Usar sempre o **gabarito definitivo** (não o preliminar) — questões anuladas e alteradas
  importam para a análise.

Alvo pós-MVP: tribunais (TRT/TRF/TJ/TSE/STJ/STF/TST), carreira fiscal (RFB, SEFAZ, ISS),
carreiras jurídicas de entrada.

## Fases do projeto

- **Fase 0** — Setup e decisões de recorte ✅ concluída em 2026-07-04
- **Fase 1** — ✅ concluída em 2026-07-04 — Coleta (download PDFs oficiais) e extração (segmentação questão a questão,
  com texto motivador; SQLite; relatório de qualidade da extração por prova)
- **Fase 2** — Taxonomia a partir dos editais PF/PRF (revisada pelo usuário antes de usar)
  + classificação em 2 níveis (tópico e subtópico), 100% local, em camadas:
  Camada 1 = regras determinísticas (referências normativas + termos técnicos);
  Camada 2 = TF-IDF (n-gramas 1-3) + classificador linear scikit-learn treinado
  nos rótulos da Camada 1 + revisões manuais, com validação cruzada e métricas
  por tópico; Camada 3 (opcional, só se métricas insuficientes) = embeddings
  locais sentence-transformers em CPU. Registrar confiança e origem de cada
  rótulo; fluxo de revisão manual realimenta o treino (active learning simples).
- **Fase 3** — Estatística descritiva, análise do estilo CEBRASPE (proporção certo/errado
  por tópico, padrões de pegadinha), modelo preditivo simples e interpretável (frequência
  ponderada por recência + suavização bayesiana; SEM redes neurais), sinal de mudanças
  legislativas (curadoria manual no início). Saída: ranking com incerteza.
- **Fase 4** — Gerador de plano de estudos (ciclos de estudo), exportação Markdown e PDF.
- **Fase 5** — Dashboard web local (Streamlit vs React: decisão do usuário), só após
  fases anteriores validadas.
- **Fase 6** — Expansão: FGV, FCC, múltipla escolha, demais disciplinas.

## Decisões tomadas

- (Fase 0, 2026-07-04) Estrutura de pastas criada; git inicializado.
- (Fase 0, 2026-07-04) **Recorte temporal: 2013 em diante.** Concursos do piloto:
  PRF 2013, PF 2018, PRF 2018/19, PF 2021, PRF 2021. PF 2012 e PF 2014 (Delegado)
  ficam de fora (legislação/estilo defasados).
- (Fase 0, 2026-07-04) **Cargos do piloto: Agente, Escrivão e Papiloscopista PF +
  Policial Rodoviário Federal.** Delegado excluído (perfil jurídico muito mais profundo
  distorceria o perfil estatístico dos cargos de entrada).
- (Fase 0, 2026-07-04) **Classificação LLM aprovada**: usuário tem chave da API Anthropic.
  Chave vai em `.env` (nunca commitada). Usuário controla custo escolhendo modelo e lote.
- (Fase 1, 2026-07-04) **Fonte de enumeração de arquivos**: API oficial
  `apis.cebraspe.org.br/cebraspe/eventos/{slug}` (mesma que o site usa); downloads pelo
  CDN oficial `cdn.cebraspe.org.br`. PRF 2013 usa slug legado `DPRF_13`.
- (Fase 1, 2026-07-04) **Ambiente Python via uv** (não havia Python clássico na máquina);
  `.venv/` criado com CPython 3.14, deps via `uv pip install -r requirements.txt`.
- (Fase 1, 2026-07-04) **Segmentação dos cadernos** usa 3 sinais: layout (recuo das
  linhas), tipografia (número de item tem fonte >= 7pt; numeração de linha de texto
  motivador tem 5-6pt) e sequência estrita (só aceita o próximo número esperado).
- (Fase 2, 2026-07-04) **Taxonomia consolidada v1.0 APROVADA pelo usuário**
  ("aprovo os defaults"): D1 Penal separado de Processual Penal; D2 Legislação
  Penal Especial como disciplina própria; D3 nível fino só nas 3 disciplinas de
  Direito; D4 controle de constitucionalidade mantido como raro. Detalhes em
  `docs/taxonomia_proposta.md`; esquema em `config/taxonomias/consolidada.json`.
- (Fase 2, 2026-07-04) **Regras do baseline**: âncoras casam com fronteira de
  palavra (nunca substring); referências legais e frases multi-palavra pesam 2x;
  âncora casada só no texto motivador vale metade (o item é o objeto, o motivador
  é contexto); confiança = 1 - 0.5^score.

## Estado da Fase 2 (em andamento, 100% local)

- Mapeamento item→disciplina RODADO: 869/1072 itens (81%) com `itens.disciplina`
  (`python -m src.classificacao.disciplinas`). Etapas: âncoras restritas às
  disciplinas do edital do concurso; voto majoritário por bloco com o guard
  "motivador sozinho não decide disciplina jurídica" (as provas ambientam
  RLM/Estatística em narrativas policiais — vocabulário jurídico no motivador
  é evidência fraca); interpolação entre faixas vizinhas iguais. 203 itens
  sem sinal ficam NULL.
- Camada 1 (regras) RODADA: 218/1072 itens, 111 em baixa confiança.
- Camada 2 (modelo local) RODADA: `python -m src.classificacao.modelo`,
  TF-IDF 1-3gramas + regressão logística. Validação cruzada: disciplina 93%
  de acurácia (15 classes); tópico fino 67% (9 classes, 84 exemplos). Com
  limiares honestos (0.60/0.50) o modelo NÃO grava previsões para o resíduo —
  os 203 itens sem disciplina não têm sinal textual aproveitável (fórmulas
  mutiladas, itens curtos). Métricas: `relatorios/metricas_classificador.md`.
- **Nível fino: volume de dados NÃO sustenta subtópico** (registrado conforme
  combinado). Modelo B prevê só tópico; subtópico vem de regras + revisão.
  Várias classes de tópico têm < 4 exemplos e ficaram fora do treino.
- Fluxo de revisão manual pronto: `python -m src.classificacao.revisao`
  (cada correção realimenta o treino da Camada 2 — retreinar depois).
- Pendente de decisão do usuário: estratégia para os 203 itens sem disciplina
  (revisão manual rápida vs Camada 3 embeddings vs inferência pela ordem do
  edital).

## Limitações conhecidas (Fase 1)

- **Status 'alterada' não detectável**: o gabarito definitivo do CEBRASPE só marca
  anulados (X). Detectar gabarito alterado exigiria o preliminar, que a banca tira do ar.
  O schema suporta o status; a detecção fica para quando houver fonte.
- **Itens só-figura** (ex.: PRF 2019 itens 24-26, vistas de sólidos em RLM) recebem
  placeholder "[item com conteúdo gráfico não extraível do PDF]". Irrelevante para as
  disciplinas piloto (Direito não tem itens só-figura nessas provas).
- **Fórmulas matemáticas** com subscritos saem truncadas (afeta itens de RLM/Física,
  fora das disciplinas piloto).
- Coluna `disciplina` dos itens ainda NULL — o mapeamento item→disciplina é o primeiro
  passo da Fase 2 (junto com a taxonomia dos editais).

## Estado dos dados (Fase 1)

- 23 PDFs oficiais em `data/raw/` (9 provas, 9 gabaritos definitivos, 5 editais).
- `data/processed/bancas.db`: 5 concursos, 9 provas, **1.072 itens** (45 anulados),
  342 textos motivadores. Extração 9/9 sem divergência vs gabarito definitivo
  (ver `relatorios/qualidade_extracao.md`).
- Pipelines idempotentes: `python -m src.coleta.download` e
  `python -m src.extracao.pipeline` podem rodar de novo sem duplicar nada.

## Estrutura de pastas

```
src/coleta/         # download de PDFs oficiais (delays, user-agent, cache local)
src/extracao/       # PDF → texto estruturado, segmentação por item
src/classificacao/  # taxonomia + classificadores (regras e LLM)
src/analise/        # estatística descritiva e modelo preditivo
src/plano/          # gerador de plano de estudos
tests/              # testes das funções frágeis (extração e classificação)
data/raw/           # PDFs originais (provas, gabaritos, editais) — cache, nunca re-baixar
data/processed/     # SQLite e derivados
docs/               # documentação, taxonomias propostas
relatorios/         # relatórios de qualidade de extração e saídas de análise
```

## Stack e convenções

- Python 3.11+, ambiente virtual em `.venv/`, `requirements.txt` atualizado a cada
  dependência nova
- SQLite para dados, pandas para análise, matplotlib/plotly para gráficos
- Código modular em `src/`, docstrings e comentários **em português**
- Commits git pequenos e descritivos a cada etapa concluída
- Schema do banco preparado desde o início para: banca, órgão, concurso, ano, cargo,
  disciplina, questão/item, texto motivador, formato (certo/errado ou múltipla escolha),
  gabarito, status (válida, anulada, alterada)

## Regras de trabalho

1. Trabalhar fase por fase; ao final de cada fase, apresentar resultado, testar junto com
   o usuário e só então avançar. Atualizar este CLAUDE.md ao fechar cada fase.
2. Decisões técnicas com mais de um caminho razoável: apresentar opções com prós e
   contras, não decidir sozinho.
3. Priorizar robustez do pipeline de dados sobre features. Dado ruim invalida tudo depois.
4. Dúvidas jurídicas finas → fluxo de revisão manual, nunca assumir.
