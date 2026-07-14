# Métricas do classificador local (Camada 2)

Gerado em 2026-07-14 16:00. Validação cruzada estratificada
sobre o conjunto de treino (rótulos da Camada 1 com confiança >= 0.75 +
revisões manuais). Reexecutar após cada rodada de revisão:
`python -m src.classificacao.modelo`.

## Modelo A — disciplina (todos os itens)

Previsões gravadas nesta execução: 2 (limiar 0.6).

```
                                         precision    recall  f1-score   support

                          Administração       0.84      0.93      0.88        57
Administração Financeira e Orçamentária       0.75      0.60      0.67         5
              Atividade de Inteligência       0.64      1.00      0.78         7
                          Contabilidade       0.93      1.00      0.96       102
                 Direito Administrativo       0.81      0.89      0.85        98
       Direito Civil e Processual Civil       0.96      0.88      0.92        26
                 Direito Constitucional       0.93      0.75      0.83       295
                      Direito Eleitoral       0.95      0.90      0.93        21
                          Direito Penal       0.82      0.78      0.80       109
               Direito Processual Penal       0.72      0.84      0.77        63
                       Direitos Humanos       0.85      0.97      0.90        62
                            Estatística       0.98      1.00      0.99        64
                         Execução Penal       0.97      0.94      0.96        35
                                 Física       0.96      0.89      0.92        27
                            Geopolítica       0.83      0.83      0.83         6
                            Informática       0.93      0.96      0.95       272
               Legislação Institucional       1.00      1.00      1.00         9
              Legislação Penal Especial       0.55      0.52      0.53        23
                 Legislação de Trânsito       0.69      0.92      0.79        52
                      Língua Portuguesa       0.98      0.98      0.98       369
                                 Outros       1.00      0.92      0.96        12
           Raciocínio Lógico-Matemático       1.00      0.92      0.96       121
               Ética no Serviço Público       0.70      1.00      0.82         7

                               accuracy                           0.90      1842
                              macro avg       0.86      0.89      0.87      1842
                           weighted avg       0.91      0.90      0.90      1842

```

## Modelo B — tópico fino (Direito Constitucional/Administrativo/Penal)

Previsões gravadas nesta execução: 0 (limiar 0.5).

**Limitação registrada**: o subtópico NÃO é previsto pelo modelo — com o
volume atual de treino, só o nível de tópico sustenta métrica decente.
Subtópicos vêm da Camada 1 (regras) e da revisão manual.

```
                                                                      precision    recall  f1-score   support

                           Direito Administrativo > Agentes públicos       0.70      0.52      0.60        27
                       Direito Administrativo > Atos administrativos       0.60      0.43      0.50         7
          Direito Administrativo > Controle da administração pública       0.75      0.55      0.63        11
                 Direito Administrativo > Improbidade administrativa       0.50      1.00      0.67         4
                     Direito Administrativo > Licitações e contratos       0.60      0.86      0.71         7
                 Direito Administrativo > Organização administrativa       0.58      0.78      0.67         9
                    Direito Administrativo > Poderes administrativos       0.33      0.60      0.43         5
                          Direito Administrativo > Serviços públicos       0.57      0.80      0.67         5
       Direito Constitucional > Defesa do Estado e segurança pública       0.76      0.90      0.83        29
          Direito Constitucional > Direitos e garantias fundamentais       0.57      0.48      0.52        33
                               Direito Constitucional > Ordem social       0.83      0.83      0.83        12
                      Direito Constitucional > Organização do Estado       0.61      0.58      0.59        38
                    Direito Constitucional > Organização dos poderes       0.75      0.50      0.60        72
Direito Constitucional > Teoria da Constituição e poder constituinte       0.27      0.60      0.38         5
               Direito Penal > Crimes contra a Administração Pública       0.70      1.00      0.82         7
                              Direito Penal > Crimes contra a pessoa       0.60      0.86      0.71         7
                          Direito Penal > Crimes contra o patrimônio       0.60      0.60      0.60         5
                 Direito Penal > Princípios e aplicação da lei penal       0.71      0.83      0.77         6
                                        Direito Penal > Punibilidade       0.57      0.80      0.67         5
                       Direito Penal > Teoria do crime — fato típico       0.35      0.60      0.44        10

                                                            accuracy                           0.63       304
                                                           macro avg       0.60      0.71      0.63       304
                                                        weighted avg       0.66      0.63      0.63       304

Classes fora do treino (menos de 4 exemplos): Direito Administrativo > Regime jurídico-administrativo e princípios, Direito Administrativo > Responsabilidade civil do Estado, Direito Constitucional > Controle de constitucionalidade, Direito Penal > Crimes contra a fé pública, Direito Penal > Ilicitude

```
