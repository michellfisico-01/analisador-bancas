# Analisador Preditivo de Bancas

Ciência de dados aplicada a provas de concursos públicos brasileiros:
extrai provas oficiais das bancas (CEBRASPE e FGV), classifica cada item na taxonomia do
edital e estima **a probabilidade de cada tópico ser cobrado no próximo
concurso** — com intervalo de incerteza — para gerar planos de estudo
priorizados.

**Piloto**: PF (Agente, Escrivão, Papiloscopista) e PRF, 2013-2021, nas
disciplinas de Direito Constitucional, Administrativo e Penal — já expandido
para PCDF, DEPEN, ABIN, TSE Unificado 2024 e TRF1 2024 (FGV).
**Landing page**: <https://michellfisico-01.github.io/analisador-bancas/>
**Custo zero**: 100% local, só bibliotecas de código aberto — nenhuma API
paga, nenhum serviço em nuvem.

## Por quê

Cursinhos tratam o edital como lista plana. Os dados mostram outra coisa:
em Direito Constitucional no piloto, *Direitos e garantias fundamentais*
concentra ~33% dos itens, enquanto *Controle de constitucionalidade*
praticamente não cai para cargos de entrada — e o perfil muda entre PF e
PRF. Estudar orientado por essas distribuições otimiza anos de preparação.

## Instalação

Requer Python 3.11+ (o projeto usa [uv](https://docs.astral.sh/uv/), mas
qualquer gerenciador serve):

```bash
uv venv .venv
uv pip install -r requirements.txt --python .venv
```

## Pipeline completo (idempotente, nesta ordem)

```bash
python -m src.coleta.download            # baixa PDFs oficiais (cache local)
python -m src.extracao.pipeline          # PDF -> SQLite + relatório de qualidade
python -m src.classificacao.disciplinas  # mapeia item -> disciplina
python -m src.classificacao.ordem_edital # preenche buracos pela ordem do edital
python -m src.classificacao.regras       # Camada 1: regras determinísticas
python -m src.classificacao.modelo       # Camada 2: TF-IDF + logística (métricas CV)
python -m src.analise.descritiva         # frequências, anulação, estilo CEBRASPE
python -m src.analise.preditivo          # ranking bayesiano com IC90
python -m src.analise.pegadinhas         # marcadores de pegadinha: teste estatístico
python -m src.plano.gerador --orgao PF --semanas 12 --horas-semana 20
```

Dashboard interativo:

```bash
streamlit run streamlit_app.py
```

Revisão manual (cada correção realimenta o treino da Camada 2):

```bash
python -m src.classificacao.revisao
```

## Como funciona

| Etapa | Método |
|---|---|
| Coleta | API oficial do CEBRASPE + CDN; só gabaritos definitivos; delays e user-agent identificado |
| Extração | pdfplumber; segmentação por layout + tipografia + sequência; validação cruzada com o gabarito (23/23 provas sem divergência) |
| Classificação | Camadas: regras determinísticas (âncoras normativas) → TF-IDF + regressão logística → revisão humana. Confiança e origem registradas por rótulo |
| Predição | Contagens ponderadas por recência (meia-vida 5 anos) + posterior Dirichlet (prior de Jeffreys) + sinal de mudanças legislativas com curadoria manual; IC de credibilidade 90% |
| Plano | Horas ∝ peso da disciplina × probabilidade do tópico; ciclos semanais; export Markdown/PDF |

Princípio de projeto: **nenhum número sem explicação e nenhuma cobertura
escondida** — todo relatório declara quanto do dado está rotulado e com
qual confiança.

## Estrutura

```
src/coleta/          download dos PDFs oficiais
src/extracao/        PDF -> SQLite (itens, motivadores, gabaritos)
src/classificacao/   taxonomia, regras, modelo local, revisão
src/analise/         descritiva, preditivo, pegadinhas
src/plano/           gerador de plano de estudos (MD + PDF)
config/              manifesto de coleta, taxonomias, eventos legislativos
relatorios/          saídas geradas (qualidade, métricas, rankings, planos)
tests/               32 testes das partes frágeis
```

## Dados

Exclusivamente documentos públicos oficiais publicados pela banca
(provas, gabaritos definitivos e editais). Nenhum scraping de plataformas
privadas.
