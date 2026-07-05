# Ranking preditivo de tópicos — CEBRASPE PF/PRF
Gerado em 2026-07-05 00:07. Ano de referência: 2021.

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

### Direito Constitucional (Geral) — 73 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:--------------------|
| Direitos e garantias fundamentais           |  0.33  | [0.227, 0.439] |        16.7 |        26 | —                   |
| Organização do Estado                       |  0.208 | [0.124, 0.306] |        10.4 |        14 | —                   |
| Defesa do Estado e segurança pública        |  0.158 | [0.084, 0.247] |         7.7 |        10 | —                   |
| Organização dos poderes                     |  0.151 | [0.078, 0.239] |         7.4 |        14 | —                   |
| Ordem social                                |  0.121 | [0.057, 0.203] |         5.8 |         7 | —                   |
| Teoria da Constituição e poder constituinte |  0.022 | [0.002, 0.063] |         0.7 |         2 | —                   |
| Controle de constitucionalidade             |  0.01  | [0.000, 0.037] |         0   |         0 | —                   |

### Direito Administrativo (Geral) — 33 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:----------------------------------------------------|
| Agentes públicos                            |  0.272 | [0.150, 0.411] |         7.7 |        12 | —                                                   |
| Organização administrativa                  |  0.235 | [0.121, 0.369] |         6.6 |        10 | —                                                   |
| Controle da administração pública           |  0.116 | [0.038, 0.222] |         3   |         3 | —                                                   |
| Poderes administrativos                     |  0.116 | [0.038, 0.222] |         3   |         3 | —                                                   |
| Improbidade administrativa                  |  0.06  | [0.010, 0.144] |         0.3 |         1 | Reforma da Lei de Improbidade (Lei 14.230/2021) (*) |
| Serviços públicos                           |  0.052 | [0.007, 0.131] |         1.1 |         2 | —                                                   |
| Licitações e contratos                      |  0.05  | [0.006, 0.126] |         0   |         0 | Nova Lei de Licitações (Lei 14.133/2021) (*)        |
| Atos administrativos                        |  0.042 | [0.004, 0.113] |         0.8 |         1 | —                                                   |
| Responsabilidade civil do Estado            |  0.042 | [0.004, 0.113] |         0.8 |         1 | —                                                   |
| Regime jurídico-administrativo e princípios |  0.017 | [0.000, 0.063] |         0   |         0 | —                                                   |

### Direito Penal (Geral) — 23 itens rotulados

| topico                                |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                |
|:--------------------------------------|-------:|:---------------|------------:|----------:|:-------------------------------------------------|
| Teoria do crime — fato típico         |  0.208 | [0.083, 0.365] |         3.8 |         5 | —                                                |
| Crimes contra o patrimônio            |  0.166 | [0.056, 0.313] |         3   |         5 | —                                                |
| Crimes contra a pessoa                |  0.144 | [0.043, 0.284] |         2.5 |         5 | —                                                |
| Crimes contra a Administração Pública |  0.111 | [0.025, 0.240] |         1.3 |         2 | Lei de Abuso de Autoridade (Lei 13.869/2019) (*) |
| Punibilidade                          |  0.096 | [0.018, 0.217] |         1   |         1 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Ilicitude                             |  0.076 | [0.010, 0.187] |         1.1 |         2 | —                                                |
| Crimes contra a fé pública            |  0.072 | [0.009, 0.180] |         1   |         1 | —                                                |
| Princípios e aplicação da lei penal   |  0.064 | [0.006, 0.167] |         0.3 |         1 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Culpabilidade                         |  0.04  | [0.001, 0.124] |         0.3 |         1 | —                                                |
| Outros crimes em espécie              |  0.024 | [0.000, 0.091] |         0   |         0 | —                                                |

## PF

### Direito Constitucional (PF) — 30 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:--------------------|
| Direitos e garantias fundamentais           |  0.31  | [0.175, 0.460] |         8   |         9 | —                   |
| Defesa do Estado e segurança pública        |  0.224 | [0.108, 0.364] |         5.6 |         7 | —                   |
| Ordem social                                |  0.176 | [0.073, 0.306] |         4.3 |         5 | —                   |
| Organização do Estado                       |  0.163 | [0.064, 0.290] |         4   |         6 | —                   |
| Organização dos poderes                     |  0.091 | [0.022, 0.193] |         2   |         3 | —                   |
| Controle de constitucionalidade             |  0.018 | [0.000, 0.070] |         0   |         0 | —                   |
| Teoria da Constituição e poder constituinte |  0.018 | [0.000, 0.070] |         0   |         0 | —                   |

### Direito Administrativo (PF) — 23 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:----------------------------------------------------|
| Organização administrativa                  |  0.281 | [0.147, 0.435] |         6.6 |        10 | —                                                   |
| Agentes públicos                            |  0.243 | [0.118, 0.392] |         5.6 |         7 | —                                                   |
| Controle da administração pública           |  0.139 | [0.046, 0.264] |         3   |         3 | —                                                   |
| Poderes administrativos                     |  0.139 | [0.046, 0.264] |         3   |         3 | —                                                   |
| Improbidade administrativa                  |  0.059 | [0.007, 0.150] |         0   |         0 | Reforma da Lei de Improbidade (Lei 14.230/2021) (*) |
| Licitações e contratos                      |  0.059 | [0.007, 0.150] |         0   |         0 | Nova Lei de Licitações (Lei 14.133/2021) (*)        |
| Regime jurídico-administrativo e princípios |  0.02  | [0.000, 0.075] |         0   |         0 | —                                                   |
| Atos administrativos                        |  0.02  | [0.000, 0.075] |         0   |         0 | —                                                   |
| Serviços públicos                           |  0.02  | [0.000, 0.075] |         0   |         0 | —                                                   |
| Responsabilidade civil do Estado            |  0.02  | [0.000, 0.075] |         0   |         0 | —                                                   |

### Direito Penal (PF) — 5 itens rotulados

| topico                                |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                |
|:--------------------------------------|-------:|:---------------|------------:|----------:|:-------------------------------------------------|
| Crimes contra o patrimônio            |  0.31  | [0.105, 0.559] |         2.6 |         4 | —                                                |
| Punibilidade                          |  0.197 | [0.040, 0.424] |         1   |         1 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Crimes contra a Administração Pública |  0.099 | [0.006, 0.279] |         0   |         0 | Lei de Abuso de Autoridade (Lei 13.869/2019) (*) |
| Princípios e aplicação da lei penal   |  0.099 | [0.006, 0.279] |         0   |         0 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Teoria do crime — fato típico         |  0.049 | [0.000, 0.185] |         0   |         0 | —                                                |
| Ilicitude                             |  0.049 | [0.000, 0.185] |         0   |         0 | —                                                |
| Crimes contra a pessoa                |  0.049 | [0.000, 0.185] |         0   |         0 | —                                                |
| Culpabilidade                         |  0.049 | [0.000, 0.185] |         0   |         0 | —                                                |
| Crimes contra a fé pública            |  0.049 | [0.000, 0.185] |         0   |         0 | —                                                |
| Outros crimes em espécie              |  0.049 | [0.000, 0.185] |         0   |         0 | —                                                |

## PRF

### Direito Constitucional (PRF) — 43 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:--------------------|
| Direitos e garantias fundamentais           |  0.326 | [0.190, 0.475] |         8.7 |        17 | —                   |
| Organização do Estado                       |  0.244 | [0.125, 0.385] |         6.4 |         8 | —                   |
| Organização dos poderes                     |  0.208 | [0.098, 0.343] |         5.4 |        11 | —                   |
| Defesa do Estado e segurança pública        |  0.091 | [0.023, 0.193] |         2.1 |         3 | —                   |
| Ordem social                                |  0.071 | [0.013, 0.163] |         1.5 |         2 | —                   |
| Teoria da Constituição e poder constituinte |  0.041 | [0.003, 0.114] |         0.7 |         2 | —                   |
| Controle de constitucionalidade             |  0.018 | [0.000, 0.067] |         0   |         0 | —                   |

### Direito Administrativo (PRF) — 10 itens rotulados

| topico                                      |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                   |
|:--------------------------------------------|-------:|:---------------|------------:|----------:|:----------------------------------------------------|
| Agentes públicos                            |  0.215 | [0.058, 0.427] |         2.1 |         5 | —                                                   |
| Improbidade administrativa                  |  0.152 | [0.027, 0.345] |         0.3 |         1 | Reforma da Lei de Improbidade (Lei 14.230/2021) (*) |
| Serviços públicos                           |  0.132 | [0.019, 0.316] |         1.1 |         2 | —                                                   |
| Licitações e contratos                      |  0.125 | [0.016, 0.305] |         0   |         0 | Nova Lei de Licitações (Lei 14.133/2021) (*)        |
| Responsabilidade civil do Estado            |  0.105 | [0.010, 0.274] |         0.8 |         1 | —                                                   |
| Atos administrativos                        |  0.105 | [0.010, 0.274] |         0.8 |         1 | —                                                   |
| Organização administrativa                  |  0.042 | [0.000, 0.157] |         0   |         0 | —                                                   |
| Regime jurídico-administrativo e princípios |  0.042 | [0.000, 0.157] |         0   |         0 | —                                                   |
| Poderes administrativos                     |  0.042 | [0.000, 0.157] |         0   |         0 | —                                                   |
| Controle da administração pública           |  0.042 | [0.000, 0.157] |         0   |         0 | —                                                   |

### Direito Penal (PRF) — 18 itens rotulados

| topico                                |   prob | ic90           |   n_efetivo |   n_bruto | sinal_legislativo                                |
|:--------------------------------------|-------:|:---------------|------------:|----------:|:-------------------------------------------------|
| Teoria do crime — fato típico         |  0.252 | [0.102, 0.435] |         3.8 |         5 | —                                                |
| Crimes contra a pessoa                |  0.174 | [0.052, 0.339] |         2.5 |         5 | —                                                |
| Crimes contra a Administração Pública |  0.135 | [0.031, 0.287] |         1.3 |         2 | Lei de Abuso de Autoridade (Lei 13.869/2019) (*) |
| Ilicitude                             |  0.092 | [0.013, 0.225] |         1.1 |         2 | —                                                |
| Crimes contra a fé pública            |  0.087 | [0.011, 0.217] |         1   |         1 | —                                                |
| Princípios e aplicação da lei penal   |  0.077 | [0.008, 0.201] |         0.3 |         1 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Punibilidade                          |  0.058 | [0.003, 0.168] |         0   |         0 | Pacote Anticrime (Lei 13.964/2019) (*)           |
| Culpabilidade                         |  0.048 | [0.002, 0.150] |         0.3 |         1 | —                                                |
| Crimes contra o patrimônio            |  0.048 | [0.002, 0.150] |         0.3 |         1 | —                                                |
| Outros crimes em espécie              |  0.029 | [0.000, 0.110] |         0   |         0 | —                                                |
