# Padrões de "pegadinha" — CEBRASPE PF/PRF

Gerado em 2026-07-05 08:14. Itens válidos analisados:
1027 | taxa-base de ERRADO: **52.9%**.

A intuição do concurseiro diz que certos marcadores de generalização
("somente", "sempre", "prescinde"...) sinalizam item ERRADO. Aqui a
intuição vira teste estatístico: `pct_errado` entre itens com o marcador,
IC de credibilidade de 90% (prior de Jeffreys) e `lift` sobre a taxa-base.
**CONFIRMADA** = limite inferior do IC acima da taxa-base.

## Todos os itens válidos

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto       |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:----------------|
| somente / apenas / exclusivamente  |  43 |        0.674 | [0.55, 0.78] |   1.28 | CONFIRMADA      |
| independentemente                  |  17 |        0.588 | [0.39, 0.76] |   1.11 | não conclusiva  |
| prescinde / dispensa / independe   |  11 |        0.364 | [0.17, 0.61] |   0.69 | não conclusiva  |
| desde que                          |   9 |        0.667 | [0.40, 0.87] |   1.26 | amostra pequena |
| sempre                             |   5 |        0.4   | [0.13, 0.74] |   0.76 | amostra pequena |
| obrigatoriamente / necessariamente |   5 |        0.4   | [0.13, 0.74] |   0.76 | amostra pequena |
| salvo / exceto / ressalvado        |   4 |        0.75  | [0.35, 0.95] |   1.42 | amostra pequena |
| privativo / exclusivo              |   4 |        1     | [0.64, 1.00] |   1.89 | amostra pequena |
| nunca / jamais                     |   3 |        1     | [0.56, 1.00] |   1.89 | amostra pequena |
| é vedado / não se admite           |   3 |        1     | [0.56, 1.00] |   1.89 | amostra pequena |

## Só disciplinas jurídicas

Taxa-base de ERRADO nas jurídicas: 50.0%.

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto       |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:----------------|
| somente / apenas / exclusivamente  |  13 |        0.769 | [0.55, 0.91] |   1.54 | CONFIRMADA      |
| independentemente                  |   7 |        0.571 | [0.28, 0.83] |   1.14 | amostra pequena |
| desde que                          |   5 |        0.6   | [0.26, 0.87] |   1.2  | amostra pequena |
| é vedado / não se admite           |   3 |        1     | [0.56, 1.00] |   2    | amostra pequena |
| salvo / exceto / ressalvado        |   3 |        1     | [0.56, 1.00] |   2    | amostra pequena |
| obrigatoriamente / necessariamente |   2 |        1     | [0.43, 1.00] |   2    | amostra pequena |
| prescinde / dispensa / independe   |   2 |        0.5   | [0.10, 0.90] |   1    | amostra pequena |
| sempre                             |   1 |        1     | [0.23, 1.00] |   2    | amostra pequena |
| privativo / exclusivo              |   1 |        1     | [0.23, 1.00] |   2    | amostra pequena |

## % ERRADO por tópico (disciplinas piloto, n >= 8)

Tópicos no topo são onde a banca mais "arma" o item — priorize resolver
questões (não só teoria) ao estudá-los.

| disciplina             | topico                            |   n |   pct_errado | ic90         |
|:-----------------------|:----------------------------------|----:|-------------:|:-------------|
| Direito Constitucional | Organização dos poderes           |  12 |        0.667 | [0.43, 0.85] |
| Direito Constitucional | Direitos e garantias fundamentais |  25 |        0.44  | [0.29, 0.60] |
| Direito Administrativo | Agentes públicos                  |  11 |        0.364 | [0.17, 0.61] |
| Direito Constitucional | Organização do Estado             |  13 |        0.308 | [0.14, 0.53] |
| Direito Administrativo | Organização administrativa        |  10 |        0.3   | [0.12, 0.56] |
