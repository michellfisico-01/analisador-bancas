# Padrões de "pegadinha" — CEBRASPE PF/PRF

Gerado em 2026-07-14 16:01. Itens válidos analisados:
1873 | taxa-base de ERRADO: **52.7%**.

A intuição do concurseiro diz que certos marcadores de generalização
("somente", "sempre", "prescinde"...) sinalizam item ERRADO. Aqui a
intuição vira teste estatístico: `pct_errado` entre itens com o marcador,
IC de credibilidade de 90% (prior de Jeffreys) e `lift` sobre a taxa-base.
**CONFIRMADA** = limite inferior do IC acima da taxa-base.

## Todos os itens válidos

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto                  |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:---------------------------|
| somente / apenas / exclusivamente  |  90 |        0.644 | [0.56, 0.72] |   1.22 | CONFIRMADA                 |
| independentemente                  |  34 |        0.529 | [0.39, 0.66] |   1    | não conclusiva             |
| privativo / exclusivo              |  22 |        0.682 | [0.51, 0.82] |   1.29 | não conclusiva             |
| desde que                          |  21 |        0.619 | [0.44, 0.77] |   1.17 | não conclusiva             |
| prescinde / dispensa / independe   |  21 |        0.333 | [0.19, 0.51] |   0.63 | INVERTIDA (sinal de CERTO) |
| sempre                             |  19 |        0.526 | [0.34, 0.70] |   1    | não conclusiva             |
| é vedado / não se admite           |  18 |        0.667 | [0.47, 0.82] |   1.27 | não conclusiva             |
| obrigatoriamente / necessariamente |  12 |        0.667 | [0.43, 0.85] |   1.27 | não conclusiva             |
| salvo / exceto / ressalvado        |  11 |        0.727 | [0.48, 0.89] |   1.38 | não conclusiva             |
| nunca / jamais                     |   4 |        0.75  | [0.35, 0.95] |   1.42 | amostra pequena            |
| qualquer hipótese/caso             |   2 |        0.5   | [0.10, 0.90] |   0.95 | amostra pequena            |
| todos / nenhum (generalização)     |   1 |        1     | [0.23, 1.00] |   1.9  | amostra pequena            |

## Só disciplinas jurídicas

Taxa-base de ERRADO nas jurídicas: 52.4%.

| marcador                           |   n |   pct_errado | ic90         |   lift | veredicto                  |
|:-----------------------------------|----:|-------------:|:-------------|-------:|:---------------------------|
| somente / apenas / exclusivamente  |  28 |        0.679 | [0.52, 0.81] |   1.29 | CONFIRMADA                 |
| independentemente                  |  17 |        0.529 | [0.34, 0.71] |   1.01 | não conclusiva             |
| privativo / exclusivo              |  14 |        0.786 | [0.57, 0.92] |   1.5  | CONFIRMADA                 |
| é vedado / não se admite           |  11 |        0.909 | [0.69, 0.98] |   1.73 | CONFIRMADA                 |
| prescinde / dispensa / independe   |  11 |        0.273 | [0.11, 0.52] |   0.52 | INVERTIDA (sinal de CERTO) |
| desde que                          |   8 |        0.5   | [0.24, 0.76] |   0.95 | amostra pequena            |
| salvo / exceto / ressalvado        |   7 |        0.857 | [0.56, 0.97] |   1.63 | amostra pequena            |
| obrigatoriamente / necessariamente |   3 |        1     | [0.56, 1.00] |   1.91 | amostra pequena            |
| sempre                             |   3 |        0.667 | [0.24, 0.94] |   1.27 | amostra pequena            |
| qualquer hipótese/caso             |   1 |        1     | [0.23, 1.00] |   1.91 | amostra pequena            |
| todos / nenhum (generalização)     |   1 |        1     | [0.23, 1.00] |   1.91 | amostra pequena            |

## % ERRADO por tópico (disciplinas piloto, n >= 8)

Tópicos no topo são onde a banca mais "arma" o item — priorize resolver
questões (não só teoria) ao estudá-los.

| disciplina             | topico                               |   n |   pct_errado | ic90         |
|:-----------------------|:-------------------------------------|----:|-------------:|:-------------|
| Direito Constitucional | Direitos e garantias fundamentais    |  21 |        0.619 | [0.44, 0.77] |
| Direito Constitucional | Organização do Estado                |  21 |        0.619 | [0.44, 0.77] |
| Direito Constitucional | Defesa do Estado e segurança pública |  15 |        0.533 | [0.33, 0.73] |
| Direito Administrativo | Agentes públicos                     |  11 |        0.455 | [0.23, 0.69] |
| Direito Constitucional | Organização dos poderes              |  37 |        0.432 | [0.31, 0.57] |
