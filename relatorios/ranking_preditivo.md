# Ranking preditivo de tópicos — CEBRASPE PF/PRF
Gerado em 2026-07-14 15:06. Ano de referência: 2021.

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

### Direito Constitucional (Geral) — 71 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:--------------------|
| Defesa do Estado e segurança pública        |  0.279 | [0.189, 0.377] |        16.4 |        19 | —                   |
| Organização dos poderes                     |  0.24  | [0.155, 0.334] |        14   |        21 | —                   |
| Direitos e garantias fundamentais           |  0.228 | [0.145, 0.321] |        13.3 |        15 | —                   |
| Organização do Estado                       |  0.136 | [0.072, 0.214] |         7.7 |         9 | —                   |
| Ordem social                                |  0.08  | [0.032, 0.143] |         4.3 |         5 | —                   |
| Teoria da Constituição e poder constituinte |  0.03  | [0.005, 0.073] |         1.3 |         2 | —                   |
| Controle de constitucionalidade             |  0.008 | [0.000, 0.032] |         0   |         0 | —                   |

### Direito Administrativo (Geral) — 35 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:----------------------------------------------------|
| Agentes públicos                            |  0.197 | [0.099, 0.316] |         6.4 |         9 | —                                                   |
| Poderes administrativos                     |  0.157 | [0.070, 0.268] |         5   |         5 | —                                                   |
| Licitações e contratos                      |  0.157 | [0.070, 0.268] |         4   |         4 | Nova Lei de Licitações (Lei 14.133/2021) (*)        |
| Atos administrativos                        |  0.112 | [0.040, 0.210] |         3.4 |         4 | —                                                   |
| Controle da administração pública           |  0.1   | [0.033, 0.194] |         3   |         3 | —                                                   |
| Organização administrativa                  |  0.09  | [0.027, 0.180] |         2.6 |         4 | —                                                   |
| Regime jurídico-administrativo e princípios |  0.052 | [0.008, 0.124] |         1.3 |         2 | —                                                   |
| Improbidade administrativa                  |  0.052 | [0.009, 0.125] |         0.3 |         1 | Reforma da Lei de Improbidade (Lei 14.230/2021) (*) |
| Serviços públicos                           |  0.045 | [0.006, 0.114] |         1.1 |         2 | —                                                   |
| Responsabilidade civil do Estado            |  0.036 | [0.003, 0.098] |         0.8 |         1 | —                                                   |

### Direito Penal (Geral) — 22 itens rotulados

| topico                                |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                |
|:--------------------------------------|-------:|:---------------|------------:|----------:|:-------------------------------------------------|
| Crimes contra a pessoa                |  0.2   | [0.086, 0.341] |         4.5 |         5 | —                                                |
| Crimes contra o patrimônio            |  0.192 | [0.081, 0.332] |         4.3 |         5 | —                                                |
| Crimes contra a Administração Pública |  0.173 | [0.067, 0.308] |         3.3 |         4 | Lei de Abuso de Autoridade (Lei 13.869/2019) (*) |
| Punibilidade                          |  0.12  | [0.035, 0.239] |         2   |         2 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Princípios e aplicação da lei penal   |  0.093 | [0.021, 0.202] |         1.3 |         2 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Teoria do crime — fato típico         |  0.073 | [0.012, 0.172] |         1.3 |         2 | —                                                |
| Crimes contra a fé pública            |  0.06  | [0.007, 0.151] |         1   |         1 | —                                                |
| Ilicitude                             |  0.05  | [0.004, 0.135] |         0.8 |         1 | —                                                |
| Culpabilidade                         |  0.02  | [0.000, 0.076] |         0   |         0 | —                                                |
| Outros crimes em espécie              |  0.02  | [0.000, 0.076] |         0   |         0 | —                                                |

## PF

### Direito Constitucional (PF) — 21 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:--------------------|
| Defesa do Estado e segurança pública        |  0.317 | [0.158, 0.497] |         5.6 |         7 | —                   |
| Ordem social                                |  0.248 | [0.107, 0.420] |         4.3 |         5 | —                   |
| Direitos e garantias fundamentais           |  0.128 | [0.031, 0.268] |         2   |         3 | —                   |
| Organização dos poderes                     |  0.128 | [0.031, 0.268] |         2   |         3 | —                   |
| Organização do Estado                       |  0.128 | [0.031, 0.268] |         2   |         3 | —                   |
| Controle de constitucionalidade             |  0.026 | [0.000, 0.098] |         0   |         0 | —                   |
| Teoria da Constituição e poder constituinte |  0.026 | [0.000, 0.098] |         0   |         0 | —                   |

### Direito Administrativo (PF) — 16 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:----------------------------------------------------|
| Agentes públicos                            |  0.266 | [0.123, 0.435] |         5   |         6 | —                                                   |
| Poderes administrativos                     |  0.17  | [0.057, 0.319] |         3   |         3 | —                                                   |
| Controle da administração pública           |  0.17  | [0.057, 0.319] |         3   |         3 | —                                                   |
| Organização administrativa                  |  0.152 | [0.047, 0.296] |         2.6 |         4 | —                                                   |
| Improbidade administrativa                  |  0.073 | [0.009, 0.183] |         0   |         0 | Reforma da Lei de Improbidade (Lei 14.230/2021) (*) |
| Licitações e contratos                      |  0.073 | [0.009, 0.183] |         0   |         0 | Nova Lei de Licitações (Lei 14.133/2021) (*)        |
| Regime jurídico-administrativo e princípios |  0.024 | [0.000, 0.092] |         0   |         0 | —                                                   |
| Atos administrativos                        |  0.024 | [0.000, 0.092] |         0   |         0 | —                                                   |
| Serviços públicos                           |  0.024 | [0.000, 0.092] |         0   |         0 | —                                                   |
| Responsabilidade civil do Estado            |  0.024 | [0.000, 0.092] |         0   |         0 | —                                                   |

### Direito Penal (PF) — 1 itens rotulados

| topico                                |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                |
|:--------------------------------------|-------:|:---------------|------------:|----------:|:-------------------------------------------------|
| Punibilidade                          |  0.267 | [0.058, 0.550] |           1 |         1 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Princípios e aplicação da lei penal   |  0.133 | [0.008, 0.369] |           0 |         0 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Crimes contra a Administração Pública |  0.133 | [0.008, 0.369] |           0 |         0 | Lei de Abuso de Autoridade (Lei 13.869/2019) (*) |
| Teoria do crime — fato típico         |  0.067 | [0.000, 0.247] |           0 |         0 | —                                                |
| Culpabilidade                         |  0.067 | [0.000, 0.247] |           0 |         0 | —                                                |
| Ilicitude                             |  0.067 | [0.000, 0.247] |           0 |         0 | —                                                |
| Crimes contra a pessoa                |  0.067 | [0.000, 0.247] |           0 |         0 | —                                                |
| Crimes contra o patrimônio            |  0.067 | [0.000, 0.247] |           0 |         0 | —                                                |
| Crimes contra a fé pública            |  0.067 | [0.000, 0.247] |           0 |         0 | —                                                |
| Outros crimes em espécie              |  0.067 | [0.000, 0.247] |           0 |         0 | —                                                |

## PRF

### Direito Constitucional (PRF) — 17 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:--------------------|
| Organização dos poderes                     |  0.363 | [0.173, 0.576] |         4.7 |         9 | —                   |
| Direitos e garantias fundamentais           |  0.196 | [0.057, 0.385] |         2.3 |         3 | —                   |
| Organização do Estado                       |  0.157 | [0.036, 0.333] |         1.8 |         2 | —                   |
| Defesa do Estado e segurança pública        |  0.157 | [0.036, 0.333] |         1.8 |         2 | —                   |
| Teoria da Constituição e poder constituinte |  0.058 | [0.002, 0.179] |         0.3 |         1 | —                   |
| Controle de constitucionalidade             |  0.035 | [0.000, 0.131] |         0   |         0 | —                   |
| Ordem social                                |  0.035 | [0.000, 0.131] |         0   |         0 | —                   |

### Direito Administrativo (PRF) — 8 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:----------------------------------------------------|
| Agentes públicos                            |  0.169 | [0.032, 0.373] |         1.4 |         3 | —                                                   |
| Improbidade administrativa                  |  0.161 | [0.029, 0.363] |         0.3 |         1 | Reforma da Lei de Improbidade (Lei 14.230/2021) (*) |
| Serviços públicos                           |  0.14  | [0.020, 0.332] |         1.1 |         2 | —                                                   |
| Licitações e contratos                      |  0.132 | [0.017, 0.321] |         0   |         0 | Nova Lei de Licitações (Lei 14.133/2021) (*)        |
| Responsabilidade civil do Estado            |  0.111 | [0.010, 0.289] |         0.8 |         1 | —                                                   |
| Atos administrativos                        |  0.111 | [0.010, 0.289] |         0.8 |         1 | —                                                   |
| Organização administrativa                  |  0.044 | [0.000, 0.166] |         0   |         0 | —                                                   |
| Regime jurídico-administrativo e princípios |  0.044 | [0.000, 0.166] |         0   |         0 | —                                                   |
| Poderes administrativos                     |  0.044 | [0.000, 0.166] |         0   |         0 | —                                                   |
| Controle da administração pública           |  0.044 | [0.000, 0.166] |         0   |         0 | —                                                   |

### Direito Penal (PRF) — 10 itens rotulados

| topico                                |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                |
|:--------------------------------------|-------:|:---------------|------------:|----------:|:-------------------------------------------------|
| Crimes contra a Administração Pública |  0.178 | [0.042, 0.371] |         1.3 |         2 | Lei de Abuso de Autoridade (Lei 13.869/2019) (*) |
| Crimes contra a pessoa                |  0.154 | [0.031, 0.338] |         1.5 |         2 | —                                                |
| Teoria do crime — fato típico         |  0.14  | [0.024, 0.318] |         1.3 |         2 | —                                                |
| Crimes contra a fé pública            |  0.115 | [0.015, 0.281] |         1   |         1 | —                                                |
| Princípios e aplicação da lei penal   |  0.102 | [0.011, 0.261] |         0.3 |         1 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Ilicitude                             |  0.096 | [0.009, 0.252] |         0.8 |         1 | —                                                |
| Punibilidade                          |  0.076 | [0.004, 0.219] |         0   |         0 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Crimes contra o patrimônio            |  0.063 | [0.002, 0.196] |         0.3 |         1 | —                                                |
| Culpabilidade                         |  0.038 | [0.000, 0.144] |         0   |         0 | —                                                |
| Outros crimes em espécie              |  0.038 | [0.000, 0.144] |         0   |         0 | —                                                |
