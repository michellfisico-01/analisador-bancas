# Padrões de "pegadinha" — CEBRASPE PF/PRF

Gerado em 2026-07-14 15:16. Itens válidos analisados:
1798 | taxa-base de ERRADO: **52.6%**.

A intuição do concurseiro diz que certos marcadores de generalização
("somente", "sempre", "prescinde"...) sinalizam item ERRADO. Aqui a
intuição vira teste estatístico: `pct_errado` entre itens com o marcador,
IC de credibilidade de 90% (prior de Jeffreys) e `lift` sobre a taxa-base.
**CONFIRMADA** = limite inferior do IC acima da taxa-base.

## Todos os itens válidos

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto                  |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:---------------------------|
| somente / apenas / exclusivamente  |  78 |        0.679 | [0.59, 0.76] |   1.29 | CONFIRMADA                 |
| independentemente                  |  31 |        0.548 | [0.40, 0.69] |   1.04 | não conclusiva             |
| privativo / exclusivo              |  21 |        0.714 | [0.54, 0.85] |   1.36 | CONFIRMADA                 |
| prescinde / dispensa / independe   |  19 |        0.316 | [0.17, 0.50] |   0.6  | INVERTIDA (sinal de CERTO) |
| desde que                          |  18 |        0.667 | [0.47, 0.82] |   1.27 | não conclusiva             |
| é vedado / não se admite           |  17 |        0.647 | [0.45, 0.81] |   1.23 | não conclusiva             |
| sempre                             |  16 |        0.5   | [0.31, 0.69] |   0.95 | não conclusiva             |
| obrigatoriamente / necessariamente |  10 |        0.6   | [0.35, 0.81] |   1.14 | não conclusiva             |
| salvo / exceto / ressalvado        |   8 |        0.75  | [0.46, 0.92] |   1.43 | amostra pequena            |
| nunca / jamais                     |   3 |        1     | [0.56, 1.00] |   1.9  | amostra pequena            |
| qualquer hipótese/caso             |   2 |        0.5   | [0.10, 0.90] |   0.95 | amostra pequena            |
| todos / nenhum (generalização)     |   1 |        1     | [0.23, 1.00] |   1.9  | amostra pequena            |

## Só disciplinas jurídicas

Taxa-base de ERRADO nas jurídicas: 52.7%.

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto       |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:----------------|
| somente / apenas / exclusivamente  |  25 |        0.72  | [0.56, 0.85] |   1.37 | CONFIRMADA      |
| independentemente                  |  14 |        0.571 | [0.36, 0.77] |   1.08 | não conclusiva  |
| privativo / exclusivo              |  13 |        0.846 | [0.64, 0.95] |   1.61 | CONFIRMADA      |
| é vedado / não se admite           |  11 |        0.909 | [0.69, 0.98] |   1.72 | CONFIRMADA      |
| prescinde / dispensa / independe   |   9 |        0.222 | [0.07, 0.49] |   0.42 | amostra pequena |
| desde que                          |   7 |        0.714 | [0.41, 0.91] |   1.36 | amostra pequena |
| salvo / exceto / ressalvado        |   6 |        1     | [0.74, 1.00] |   1.9  | amostra pequena |
| obrigatoriamente / necessariamente |   3 |        1     | [0.56, 1.00] |   1.9  | amostra pequena |
| sempre                             |   3 |        0.667 | [0.24, 0.94] |   1.26 | amostra pequena |
| qualquer hipótese/caso             |   1 |        1     | [0.23, 1.00] |   1.9  | amostra pequena |
| todos / nenhum (generalização)     |   1 |        1     | [0.23, 1.00] |   1.9  | amostra pequena |

## % ERRADO por tópico (disciplinas piloto, n >= 8)

Tópicos no topo são onde a banca mais "arma" o item — priorize resolver
questões (não só teoria) ao estudá-los.

| disciplina             | topico                               |   n |   pct_errado | ic90         |
|:-----------------------|:-------------------------------------|----:|-------------:|:-------------|
| Direito Constitucional | Organização do Estado                |  21 |        0.619 | [0.44, 0.77] |
| Direito Constitucional | Direitos e garantias fundamentais    |  20 |        0.6   | [0.42, 0.76] |
| Direito Constitucional | Defesa do Estado e segurança pública |  15 |        0.533 | [0.33, 0.73] |
| Direito Constitucional | Organização dos poderes              |  30 |        0.467 | [0.32, 0.61] |
| Direito Administrativo | Agentes públicos                     |   8 |        0.25  | [0.08, 0.54] |
