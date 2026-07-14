# Métricas do classificador local (Camada 2)

Gerado em 2026-07-14 16:15. Validação cruzada estratificada
sobre o conjunto de treino (rótulos da Camada 1 com confiança >= 0.75 +
revisões manuais). Reexecutar após cada rodada de revisão:
`python -m src.classificacao.modelo`.

## Modelo A — disciplina (todos os itens)

Previsões gravadas nesta execução: 0 (limiar 0.6).

```
                                         precision    recall  f1-score   support

                          Administração       0.80      0.98      0.88        54
Administração Financeira e Orçamentária       0.75      0.60      0.67         5
              Atividade de Inteligência       0.50      0.67      0.57         9
                          Contabilidade       0.93      1.00      0.97        70
                 Direito Administrativo       0.79      0.87      0.83       106
       Direito Civil e Processual Civil       1.00      0.85      0.92        27
                 Direito Constitucional       0.89      0.70      0.78       288
                      Direito Eleitoral       0.95      0.90      0.93        21
                          Direito Penal       0.85      0.79      0.82       109
               Direito Processual Penal       0.82      0.87      0.84        62
                       Direitos Humanos       0.81      0.97      0.88        67
                            Estatística       1.00      1.00      1.00        43
                         Execução Penal       0.94      0.94      0.94        33
                                 Física       0.92      0.85      0.88        27
                            Geopolítica       1.00      0.83      0.91         6
                            Informática       0.91      0.97      0.94       222
               Legislação Institucional       1.00      1.00      1.00         9
              Legislação Penal Especial       0.61      0.61      0.61        23
                 Legislação de Trânsito       0.70      0.98      0.82        50
                      Língua Portuguesa       0.98      0.98      0.98       380
                                 Outros       1.00      0.94      0.97        17
           Raciocínio Lógico-Matemático       1.00      0.94      0.97       106
               Ética no Serviço Público       0.70      1.00      0.82         7

                               accuracy                           0.89      1741
                              macro avg       0.86      0.88      0.87      1741
                           weighted avg       0.90      0.89      0.89      1741

```

## Modelo B — tópico fino (Direito Constitucional/Administrativo/Penal)

Previsões gravadas nesta execução: 0 (limiar 0.5).

**Limitação registrada**: o subtópico NÃO é previsto pelo modelo — com o
volume atual de treino, só o nível de tópico sustenta métrica decente.
Subtópicos vêm da Camada 1 (regras) e da revisão manual.

```
                                                                      precision    recall  f1-score   support

                           Direito Administrativo > Agentes públicos       0.71      0.56      0.62        27
                       Direito Administrativo > Atos administrativos       0.64      0.88      0.74         8
          Direito Administrativo > Controle da administração pública       0.82      0.82      0.82        11
                 Direito Administrativo > Improbidade administrativa       0.71      1.00      0.83         5
                     Direito Administrativo > Licitações e contratos       0.62      0.89      0.73         9
                 Direito Administrativo > Organização administrativa       0.62      0.80      0.70        10
                    Direito Administrativo > Poderes administrativos       0.43      0.50      0.46         6
Direito Administrativo > Regime jurídico-administrativo e princípios       0.60      0.75      0.67         4
                          Direito Administrativo > Serviços públicos       0.50      0.40      0.44         5
       Direito Constitucional > Defesa do Estado e segurança pública       0.81      0.86      0.83        29
          Direito Constitucional > Direitos e garantias fundamentais       0.56      0.53      0.55        34
                               Direito Constitucional > Ordem social       0.50      0.62      0.55        13
                      Direito Constitucional > Organização do Estado       0.62      0.49      0.55        43
                    Direito Constitucional > Organização dos poderes       0.78      0.61      0.68        82
Direito Constitucional > Teoria da Constituição e poder constituinte       0.31      0.67      0.42         6
               Direito Penal > Crimes contra a Administração Pública       0.67      0.86      0.75         7
                              Direito Penal > Crimes contra a pessoa       0.50      0.62      0.56         8
                          Direito Penal > Crimes contra o patrimônio       0.43      0.50      0.46         6
                 Direito Penal > Princípios e aplicação da lei penal       0.83      0.83      0.83         6
                                        Direito Penal > Punibilidade       0.67      0.80      0.73         5
                       Direito Penal > Teoria do crime — fato típico       0.29      0.40      0.33        10

                                                            accuracy                           0.64       334
                                                           macro avg       0.60      0.68      0.63       334
                                                        weighted avg       0.66      0.64      0.64       334

Classes fora do treino (menos de 4 exemplos): Direito Administrativo > Responsabilidade civil do Estado, Direito Constitucional > Controle de constitucionalidade, Direito Penal > Crimes contra a fé pública, Direito Penal > Ilicitude

```
