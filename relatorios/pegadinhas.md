# Padrões de "pegadinha" — CEBRASPE PF/PRF

Gerado em 2026-07-05 08:50. Itens válidos analisados:
1313 | taxa-base de ERRADO: **53.2%**.

A intuição do concurseiro diz que certos marcadores de generalização
("somente", "sempre", "prescinde"...) sinalizam item ERRADO. Aqui a
intuição vira teste estatístico: `pct_errado` entre itens com o marcador,
IC de credibilidade de 90% (prior de Jeffreys) e `lift` sobre a taxa-base.
**CONFIRMADA** = limite inferior do IC acima da taxa-base.

## Todos os itens válidos

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto       |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:----------------|
| somente / apenas / exclusivamente  |  66 |        0.697 | [0.60, 0.78] |   1.31 | CONFIRMADA      |
| independentemente                  |  24 |        0.542 | [0.38, 0.70] |   1.02 | não conclusiva  |
| prescinde / dispensa / independe   |  16 |        0.375 | [0.20, 0.58] |   0.71 | não conclusiva  |
| privativo / exclusivo              |  14 |        0.714 | [0.50, 0.87] |   1.34 | não conclusiva  |
| desde que                          |  11 |        0.727 | [0.48, 0.89] |   1.37 | não conclusiva  |
| sempre                             |  10 |        0.6   | [0.35, 0.81] |   1.13 | não conclusiva  |
| é vedado / não se admite           |   9 |        0.778 | [0.51, 0.93] |   1.46 | amostra pequena |
| obrigatoriamente / necessariamente |   8 |        0.5   | [0.24, 0.76] |   0.94 | amostra pequena |
| salvo / exceto / ressalvado        |   6 |        0.667 | [0.34, 0.90] |   1.25 | amostra pequena |
| nunca / jamais                     |   3 |        1     | [0.56, 1.00] |   1.88 | amostra pequena |
| qualquer hipótese/caso             |   1 |        1     | [0.23, 1.00] |   1.88 | amostra pequena |
| todos / nenhum (generalização)     |   1 |        1     | [0.23, 1.00] |   1.88 | amostra pequena |

## Só disciplinas jurídicas

Taxa-base de ERRADO nas jurídicas: 52.4%.

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto       |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:----------------|
| somente / apenas / exclusivamente  |  20 |        0.8   | [0.63, 0.91] |   1.53 | CONFIRMADA      |
| independentemente                  |  10 |        0.5   | [0.26, 0.74] |   0.95 | não conclusiva  |
| privativo / exclusivo              |   9 |        0.778 | [0.51, 0.93] |   1.48 | amostra pequena |
| é vedado / não se admite           |   8 |        0.875 | [0.60, 0.98] |   1.67 | amostra pequena |
| prescinde / dispensa / independe   |   6 |        0.333 | [0.10, 0.66] |   0.64 | amostra pequena |
| desde que                          |   6 |        0.667 | [0.34, 0.90] |   1.27 | amostra pequena |
| salvo / exceto / ressalvado        |   4 |        1     | [0.64, 1.00] |   1.91 | amostra pequena |
| obrigatoriamente / necessariamente |   2 |        1     | [0.43, 1.00] |   1.91 | amostra pequena |
| sempre                             |   1 |        1     | [0.23, 1.00] |   1.91 | amostra pequena |
| qualquer hipótese/caso             |   1 |        1     | [0.23, 1.00] |   1.91 | amostra pequena |
| todos / nenhum (generalização)     |   1 |        1     | [0.23, 1.00] |   1.91 | amostra pequena |

## % ERRADO por tópico (disciplinas piloto, n >= 8)

Tópicos no topo são onde a banca mais "arma" o item — priorize resolver
questões (não só teoria) ao estudá-los.

| disciplina             | topico                               |   n |   pct_errado | ic90         |
|:-----------------------|:-------------------------------------|----:|-------------:|:-------------|
| Direito Constitucional | Organização dos poderes              |  16 |        0.625 | [0.42, 0.80] |
| Direito Penal          | Crimes contra o patrimônio           |  12 |        0.583 | [0.35, 0.79] |
| Direito Constitucional | Defesa do Estado e segurança pública |  16 |        0.562 | [0.36, 0.75] |
| Direito Penal          | Crimes contra a pessoa               |   9 |        0.556 | [0.30, 0.79] |
| Direito Constitucional | Direitos e garantias fundamentais    |  33 |        0.485 | [0.35, 0.62] |
| Direito Administrativo | Agentes públicos                     |  12 |        0.417 | [0.21, 0.65] |
| Direito Constitucional | Organização do Estado                |  17 |        0.353 | [0.19, 0.55] |
| Direito Administrativo | Organização administrativa           |  10 |        0.3   | [0.12, 0.56] |
