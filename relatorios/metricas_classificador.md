# Métricas do classificador local (Camada 2)

Gerado em 2026-07-14 15:15. Validação cruzada estratificada
sobre o conjunto de treino (rótulos da Camada 1 com confiança >= 0.75 +
revisões manuais). Reexecutar após cada rodada de revisão:
`python -m src.classificacao.modelo`.

## Modelo A — disciplina (todos os itens)

Previsões gravadas nesta execução: 2 (limiar 0.6).

```
                                  precision    recall  f1-score   support

                   Administração       0.80      0.96      0.87        54
       Atividade de Inteligência       0.64      1.00      0.78         7
                   Contabilidade       0.96      1.00      0.98       102
          Direito Administrativo       0.83      0.85      0.84        88
Direito Civil e Processual Civil       1.00      0.82      0.90        17
          Direito Constitucional       0.91      0.76      0.82       274
               Direito Eleitoral       0.91      1.00      0.95        21
                   Direito Penal       0.88      0.84      0.86       108
        Direito Processual Penal       0.72      0.84      0.78        58
                Direitos Humanos       0.87      0.98      0.92        46
                     Estatística       0.97      1.00      0.98        64
                  Execução Penal       0.94      0.91      0.93        34
                          Física       0.91      0.74      0.82        27
                     Geopolítica       1.00      1.00      1.00         5
                     Informática       0.92      0.97      0.95       274
        Legislação Institucional       1.00      1.00      1.00         9
       Legislação Penal Especial       0.57      0.57      0.57        23
          Legislação de Trânsito       0.69      0.94      0.80        52
               Língua Portuguesa       0.99      0.97      0.98       329
    Raciocínio Lógico-Matemático       1.00      0.89      0.94       103
        Ética no Serviço Público       0.78      1.00      0.88         7

                        accuracy                           0.90      1702
                       macro avg       0.87      0.91      0.88      1702
                    weighted avg       0.91      0.90      0.90      1702

Classes fora do treino (menos de 4 exemplos): Administração Financeira e Orçamentária

```

## Modelo B — tópico fino (Direito Constitucional/Administrativo/Penal)

Previsões gravadas nesta execução: 0 (limiar 0.5).

**Limitação registrada**: o subtópico NÃO é previsto pelo modelo — com o
volume atual de treino, só o nível de tópico sustenta métrica decente.
Subtópicos vêm da Camada 1 (regras) e da revisão manual.

```
                                                                      precision    recall  f1-score   support

                           Direito Administrativo > Agentes públicos       0.76      0.59      0.67        22
                       Direito Administrativo > Atos administrativos       0.80      0.80      0.80         5
          Direito Administrativo > Controle da administração pública       1.00      0.60      0.75        10
                     Direito Administrativo > Licitações e contratos       0.67      0.86      0.75         7
                 Direito Administrativo > Organização administrativa       0.45      0.62      0.53         8
                    Direito Administrativo > Poderes administrativos       0.33      0.60      0.43         5
                          Direito Administrativo > Serviços públicos       0.33      0.40      0.36         5
       Direito Constitucional > Defesa do Estado e segurança pública       0.81      0.89      0.85        28
          Direito Constitucional > Direitos e garantias fundamentais       0.50      0.48      0.49        29
                               Direito Constitucional > Ordem social       0.75      0.38      0.50         8
                      Direito Constitucional > Organização do Estado       0.53      0.53      0.53        30
                    Direito Constitucional > Organização dos poderes       0.76      0.58      0.66        53
Direito Constitucional > Teoria da Constituição e poder constituinte       0.20      0.50      0.29         4
               Direito Penal > Crimes contra a Administração Pública       0.57      0.80      0.67         5
                              Direito Penal > Crimes contra a pessoa       0.60      0.86      0.71         7
                          Direito Penal > Crimes contra o patrimônio       0.50      0.60      0.55         5
                 Direito Penal > Princípios e aplicação da lei penal       0.71      0.83      0.77         6
                                        Direito Penal > Punibilidade       0.67      0.40      0.50         5
                       Direito Penal > Teoria do crime — fato típico       0.22      0.29      0.25         7

                                                            accuracy                           0.61       249
                                                           macro avg       0.59      0.61      0.58       249
                                                        weighted avg       0.65      0.61      0.62       249

Classes fora do treino (menos de 4 exemplos): Direito Administrativo > Improbidade administrativa, Direito Administrativo > Regime jurídico-administrativo e princípios, Direito Administrativo > Responsabilidade civil do Estado, Direito Constitucional > Controle de constitucionalidade, Direito Penal > Crimes contra a fé pública, Direito Penal > Ilicitude

```
