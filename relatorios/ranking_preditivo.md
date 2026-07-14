# Ranking preditivo de tópicos — CEBRASPE PF/PRF
Gerado em 2026-07-14 16:16. Ano de referência: 2024.

**Como ler**: `prob` é a probabilidade estimada de um item da disciplina cair
naquele tópico no próximo concurso (posterior Dirichlet; contagens ponderadas
por recência com meia-vida de 5 anos; prior 0.5 por
tópico do edital). `ic90` é o intervalo de credibilidade de 90%: intervalo
largo = pouca evidência. `sinal_legislativo` marca tópicos com mudança legal
recente (curadoria em `config/eventos_legislativos.json`; `(*)` = entrada
ainda não revisada pelo usuário).

**Cobertura**: o ranking usa só itens com rótulo fino de tópico — a cobertura
por disciplina está em `analise_descritiva.md` e melhora a cada rodada de
revisão manual (`python -m src.classificacao.revisao`).

## Geral (PF + PRF)

### Direito Constitucional (Geral) — 140 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:--------------------|
| Organização dos poderes                     |  0.379 | [0.304, 0.456] |        41.2 |        53 | —                   |
| Organização do Estado                       |  0.205 | [0.145, 0.271] |        22.1 |        26 | —                   |
| Direitos e garantias fundamentais           |  0.175 | [0.119, 0.238] |        18.8 |        25 | —                   |
| Defesa do Estado e segurança pública        |  0.121 | [0.074, 0.175] |        12.8 |        21 | —                   |
| Ordem social                                |  0.049 | [0.020, 0.086] |         4.8 |         7 | —                   |
| Teoria da Constituição e poder constituinte |  0.04  | [0.015, 0.074] |         3.9 |         5 | —                   |
| Controle de constitucionalidade             |  0.032 | [0.010, 0.063] |         3   |         3 | —                   |

### Direito Administrativo (Geral) — 57 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:----------------------------------------------------|
| Agentes públicos                            |  0.189 | [0.103, 0.290] |         8.2 |        13 | —                                                   |
| Licitações e contratos                      |  0.162 | [0.083, 0.258] |         6.6 |         8 | Nova Lei de Licitações (Lei 14.133/2021) (*)        |
| Organização administrativa                  |  0.135 | [0.063, 0.225] |         5.7 |         8 | —                                                   |
| Atos administrativos                        |  0.125 | [0.056, 0.212] |         5.3 |         7 | —                                                   |
| Poderes administrativos                     |  0.104 | [0.042, 0.186] |         4.3 |         6 | —                                                   |
| Improbidade administrativa                  |  0.088 | [0.032, 0.165] |         3.2 |         4 | Reforma da Lei de Improbidade (Lei 14.230/2021) (*) |
| Controle da administração pública           |  0.075 | [0.024, 0.148] |         3   |         4 | —                                                   |
| Regime jurídico-administrativo e princípios |  0.073 | [0.023, 0.144] |         2.9 |         4 | —                                                   |
| Serviços públicos                           |  0.026 | [0.002, 0.073] |         0.7 |         2 | —                                                   |
| Responsabilidade civil do Estado            |  0.022 | [0.001, 0.064] |         0.5 |         1 | —                                                   |

### Direito Penal (Geral) — 39 itens rotulados

| topico                                |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                |
|:--------------------------------------|-------:|:---------------|------------:|----------:|:-------------------------------------------------|
| Crimes contra a Administração Pública |  0.169 | [0.078, 0.282] |         5.2 |         7 | Lei de Abuso de Autoridade (Lei 13.869/2019) (*) |
| Crimes contra a pessoa                |  0.157 | [0.070, 0.268] |         5   |         7 | —                                                |
| Teoria do crime — fato típico         |  0.155 | [0.068, 0.264] |         4.9 |         6 | —                                                |
| Crimes contra o patrimônio            |  0.125 | [0.048, 0.227] |         3.9 |         6 | —                                                |
| Punibilidade                          |  0.115 | [0.041, 0.214] |         3.3 |         4 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Princípios e aplicação da lei penal   |  0.102 | [0.034, 0.197] |         2.9 |         4 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Ilicitude                             |  0.086 | [0.025, 0.175] |         2.5 |         3 | —                                                |
| Crimes contra a fé pública            |  0.062 | [0.013, 0.140] |         1.7 |         2 | —                                                |
| Culpabilidade                         |  0.014 | [0.000, 0.055] |         0   |         0 | —                                                |
| Outros crimes em espécie              |  0.014 | [0.000, 0.055] |         0   |         0 | —                                                |

## PF

### Direito Constitucional (PF) — 21 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:--------------------|
| Defesa do Estado e segurança pública        |  0.302 | [0.124, 0.513] |         3.7 |         7 | —                   |
| Ordem social                                |  0.239 | [0.082, 0.441] |         2.8 |         5 | —                   |
| Direitos e garantias fundamentais           |  0.129 | [0.022, 0.297] |         1.3 |         3 | —                   |
| Organização dos poderes                     |  0.129 | [0.022, 0.297] |         1.3 |         3 | —                   |
| Organização do Estado                       |  0.129 | [0.022, 0.297] |         1.3 |         3 | —                   |
| Controle de constitucionalidade             |  0.036 | [0.000, 0.135] |         0   |         0 | —                   |
| Teoria da Constituição e poder constituinte |  0.036 | [0.000, 0.135] |         0   |         0 | —                   |

### Direito Administrativo (PF) — 16 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:----------------------------------------------------|
| Agentes públicos                            |  0.258 | [0.097, 0.457] |         3.3 |         6 | —                                                   |
| Poderes administrativos                     |  0.169 | [0.043, 0.347] |         2   |         3 | —                                                   |
| Controle da administração pública           |  0.169 | [0.043, 0.347] |         2   |         3 | —                                                   |
| Organização administrativa                  |  0.153 | [0.034, 0.325] |         1.7 |         4 | —                                                   |
| Improbidade administrativa                  |  0.058 | [0.002, 0.178] |         0   |         0 | Reforma da Lei de Improbidade (Lei 14.230/2021) (*) |
| Licitações e contratos                      |  0.058 | [0.002, 0.178] |         0   |         0 | Nova Lei de Licitações (Lei 14.133/2021) (*)        |
| Regime jurídico-administrativo e princípios |  0.034 | [0.000, 0.129] |         0   |         0 | —                                                   |
| Atos administrativos                        |  0.034 | [0.000, 0.129] |         0   |         0 | —                                                   |
| Serviços públicos                           |  0.034 | [0.000, 0.129] |         0   |         0 | —                                                   |
| Responsabilidade civil do Estado            |  0.034 | [0.000, 0.129] |         0   |         0 | —                                                   |

### Direito Penal (PF) — 1 itens rotulados

| topico                                |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                |
|:--------------------------------------|-------:|:---------------|------------:|----------:|:-------------------------------------------------|
| Punibilidade                          |  0.216 | [0.025, 0.515] |         0.7 |         1 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Princípios e aplicação da lei penal   |  0.109 | [0.002, 0.353] |         0   |         0 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Crimes contra a Administração Pública |  0.109 | [0.002, 0.353] |         0   |         0 | Lei de Abuso de Autoridade (Lei 13.869/2019) (*) |
| Teoria do crime — fato típico         |  0.081 | [0.000, 0.297] |         0   |         0 | —                                                |
| Culpabilidade                         |  0.081 | [0.000, 0.297] |         0   |         0 | —                                                |
| Ilicitude                             |  0.081 | [0.000, 0.297] |         0   |         0 | —                                                |
| Crimes contra a pessoa                |  0.081 | [0.000, 0.297] |         0   |         0 | —                                                |
| Crimes contra o patrimônio            |  0.081 | [0.000, 0.297] |         0   |         0 | —                                                |
| Crimes contra a fé pública            |  0.081 | [0.000, 0.297] |         0   |         0 | —                                                |
| Outros crimes em espécie              |  0.081 | [0.000, 0.297] |         0   |         0 | —                                                |

## PRF

### Direito Constitucional (PRF) — 17 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:--------------------|
| Organização dos poderes                     |  0.339 | [0.130, 0.584] |         3.1 |         9 | —                   |
| Direitos e garantias fundamentais           |  0.19  | [0.040, 0.409] |         1.5 |         3 | —                   |
| Organização do Estado                       |  0.155 | [0.024, 0.361] |         1.2 |         2 | —                   |
| Defesa do Estado e segurança pública        |  0.155 | [0.024, 0.361] |         1.2 |         2 | —                   |
| Teoria da Constituição e poder constituinte |  0.067 | [0.001, 0.218] |         0.2 |         1 | —                   |
| Controle de constitucionalidade             |  0.047 | [0.000, 0.175] |         0   |         0 | —                   |
| Ordem social                                |  0.047 | [0.000, 0.175] |         0   |         0 | —                   |

### Direito Administrativo (PRF) — 8 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:----------------------------------------------------|
| Agentes públicos                            |  0.167 | [0.021, 0.403] |         0.9 |         3 | —                                                   |
| Serviços públicos                           |  0.142 | [0.013, 0.366] |         0.7 |         2 | —                                                   |
| Improbidade administrativa                  |  0.125 | [0.009, 0.340] |         0.2 |         1 | Reforma da Lei de Improbidade (Lei 14.230/2021) (*) |
| Atos administrativos                        |  0.117 | [0.007, 0.327] |         0.5 |         1 | —                                                   |
| Responsabilidade civil do Estado            |  0.117 | [0.007, 0.327] |         0.5 |         1 | —                                                   |
| Licitações e contratos                      |  0.1   | [0.004, 0.298] |         0   |         0 | Nova Lei de Licitações (Lei 14.133/2021) (*)        |
| Organização administrativa                  |  0.058 | [0.000, 0.217] |         0   |         0 | —                                                   |
| Regime jurídico-administrativo e princípios |  0.058 | [0.000, 0.217] |         0   |         0 | —                                                   |
| Poderes administrativos                     |  0.058 | [0.000, 0.217] |         0   |         0 | —                                                   |
| Controle da administração pública           |  0.058 | [0.000, 0.217] |         0   |         0 | —                                                   |

### Direito Penal (PRF) — 10 itens rotulados

| topico                                |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                |
|:--------------------------------------|-------:|:---------------|------------:|----------:|:-------------------------------------------------|
| Crimes contra a Administração Pública |  0.157 | [0.022, 0.372] |         0.9 |         2 | Lei de Abuso de Autoridade (Lei 13.869/2019) (*) |
| Crimes contra a pessoa                |  0.152 | [0.020, 0.365] |         1   |         2 | —                                                |
| Teoria do crime — fato típico         |  0.139 | [0.016, 0.346] |         0.9 |         2 | —                                                |
| Crimes contra a fé pública            |  0.117 | [0.009, 0.313] |         0.7 |         1 | —                                                |
| Ilicitude                             |  0.101 | [0.006, 0.286] |         0.5 |         1 | —                                                |
| Princípios e aplicação da lei penal   |  0.091 | [0.004, 0.268] |         0.2 |         1 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Crimes contra o patrimônio            |  0.073 | [0.002, 0.235] |         0.2 |         1 | —                                                |
| Punibilidade                          |  0.068 | [0.001, 0.227] |         0   |         0 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Culpabilidade                         |  0.051 | [0.000, 0.190] |         0   |         0 | —                                                |
| Outros crimes em espécie              |  0.051 | [0.000, 0.190] |         0   |         0 | —                                                |
