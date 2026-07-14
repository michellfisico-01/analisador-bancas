# Padrões de "pegadinha" — CEBRASPE PF/PRF

Gerado em 2026-07-14 15:06. Itens válidos analisados:
1453 | taxa-base de ERRADO: **52.9%**.

A intuição do concurseiro diz que certos marcadores de generalização
("somente", "sempre", "prescinde"...) sinalizam item ERRADO. Aqui a
intuição vira teste estatístico: `pct_errado` entre itens com o marcador,
IC de credibilidade de 90% (prior de Jeffreys) e `lift` sobre a taxa-base.
**CONFIRMADA** = limite inferior do IC acima da taxa-base.

## Todos os itens válidos

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto       |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:----------------|
| somente / apenas / exclusivamente  |  68 |        0.676 | [0.58, 0.76] |   1.28 | CONFIRMADA      |
| independentemente                  |  25 |        0.56  | [0.40, 0.71] |   1.06 | não conclusiva  |
| privativo / exclusivo              |  17 |        0.706 | [0.51, 0.86] |   1.33 | não conclusiva  |
| prescinde / dispensa / independe   |  16 |        0.375 | [0.20, 0.58] |   0.71 | não conclusiva  |
| desde que                          |  12 |        0.75  | [0.52, 0.90] |   1.42 | não conclusiva  |
| sempre                             |  11 |        0.636 | [0.39, 0.83] |   1.2  | não conclusiva  |
| é vedado / não se admite           |   9 |        0.778 | [0.51, 0.93] |   1.47 | amostra pequena |
| obrigatoriamente / necessariamente |   8 |        0.5   | [0.24, 0.76] |   0.94 | amostra pequena |
| salvo / exceto / ressalvado        |   6 |        0.667 | [0.34, 0.90] |   1.26 | amostra pequena |
| nunca / jamais                     |   3 |        1     | [0.56, 1.00] |   1.89 | amostra pequena |
| qualquer hipótese/caso             |   1 |        1     | [0.23, 1.00] |   1.89 | amostra pequena |
| todos / nenhum (generalização)     |   1 |        1     | [0.23, 1.00] |   1.89 | amostra pequena |

## Só disciplinas jurídicas

Taxa-base de ERRADO nas jurídicas: 51.7%.

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto       |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:----------------|
| somente / apenas / exclusivamente  |  21 |        0.762 | [0.59, 0.88] |   1.47 | CONFIRMADA      |
| privativo / exclusivo              |  11 |        0.818 | [0.58, 0.95] |   1.58 | CONFIRMADA      |
| independentemente                  |  11 |        0.545 | [0.31, 0.77] |   1.06 | não conclusiva  |
| é vedado / não se admite           |   8 |        0.875 | [0.60, 0.98] |   1.69 | amostra pequena |
| prescinde / dispensa / independe   |   6 |        0.333 | [0.10, 0.66] |   0.65 | amostra pequena |
| desde que                          |   6 |        0.667 | [0.34, 0.90] |   1.29 | amostra pequena |
| salvo / exceto / ressalvado        |   4 |        1     | [0.64, 1.00] |   1.94 | amostra pequena |
| obrigatoriamente / necessariamente |   2 |        1     | [0.43, 1.00] |   1.94 | amostra pequena |
| sempre                             |   1 |        1     | [0.23, 1.00] |   1.94 | amostra pequena |
| qualquer hipótese/caso             |   1 |        1     | [0.23, 1.00] |   1.94 | amostra pequena |
| todos / nenhum (generalização)     |   1 |        1     | [0.23, 1.00] |   1.94 | amostra pequena |

## % ERRADO por tópico (disciplinas piloto, n >= 8)

Tópicos no topo são onde a banca mais "arma" o item — priorize resolver
questões (não só teoria) ao estudá-los.

| disciplina             | topico                               |   n |   pct_errado | ic90         |
|:-----------------------|:-------------------------------------|----:|-------------:|:-------------|
| Direito Constitucional | Direitos e garantias fundamentais    |  14 |        0.643 | [0.42, 0.82] |
| Direito Constitucional | Organização do Estado                |   9 |        0.556 | [0.30, 0.79] |
| Direito Constitucional | Organização dos poderes              |  19 |        0.526 | [0.34, 0.70] |
| Direito Constitucional | Defesa do Estado e segurança pública |  14 |        0.5   | [0.29, 0.71] |
| Direito Administrativo | Agentes públicos                     |   8 |        0.25  | [0.08, 0.54] |
