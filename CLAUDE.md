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

- **Fase 0** — Setup e decisões de recorte ← **EM ANDAMENTO**
- **Fase 1** — Coleta (download PDFs oficiais) e extração (segmentação questão a questão,
  com texto motivador; SQLite; relatório de qualidade da extração por prova)
- **Fase 2** — Taxonomia a partir dos editais PF/PRF (revisada pelo usuário antes de usar)
  + classificação em 2 níveis (tópico e subtópico) por duas abordagens comparáveis:
  regras/palavras-chave (baseline) e API da Anthropic (JSON estruturado, com texto
  motivador no contexto). Registrar confiança; fluxo de revisão manual das baixas.
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
- _As decisões de recorte (anos, concursos) serão registradas aqui após resposta do usuário._

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
