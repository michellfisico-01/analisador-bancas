# Métricas do classificador local (Camada 2)

Gerado em 2026-07-14 14:58. Validação cruzada estratificada
sobre o conjunto de treino (rótulos da Camada 1 com confiança >= 0.75 +
revisões manuais). Reexecutar após cada rodada de revisão:
`python -m src.classificacao.modelo`.

## Modelo A — disciplina (todos os itens)

Previsões gravadas nesta execução: 2 (limiar 0.6).

```
                              precision    recall  f1-score   support

   Atividade de Inteligência       1.00      1.00      1.00         7
               Contabilidade       0.96      1.00      0.98       102
      Direito Administrativo       0.88      0.79      0.83        63
      Direito Constitucional       0.88      0.83      0.85       204
               Direito Penal       0.86      0.71      0.78        76
    Direito Processual Penal       0.73      0.83      0.78        53
            Direitos Humanos       0.80      0.97      0.88        29
                 Estatística       0.97      1.00      0.98        64
              Execução Penal       0.94      0.94      0.94        34
                      Física       0.96      0.93      0.94        27
                 Geopolítica       1.00      1.00      1.00         5
                 Informática       0.96      0.97      0.96       268
    Legislação Institucional       1.00      1.00      1.00         9
   Legislação Penal Especial       0.70      0.61      0.65        23
      Legislação de Trânsito       0.70      0.92      0.79        52
           Língua Portuguesa       0.99      0.97      0.98       236
Raciocínio Lógico-Matemático       0.99      0.95      0.97       105
    Ética no Serviço Público       0.78      1.00      0.88         7

                    accuracy                           0.91      1364
                   macro avg       0.89      0.91      0.90      1364
                weighted avg       0.92      0.91      0.91      1364

```

## Modelo B — tópico fino (Direito Constitucional/Administrativo/Penal)

Previsões gravadas nesta execução: 0 (limiar 0.5).

**Limitação registrada**: o subtópico NÃO é previsto pelo modelo — com o
volume atual de treino, só o nível de tópico sustenta métrica decente.
Subtópicos vêm da Camada 1 (regras) e da revisão manual.

```
                                                               precision    recall  f1-score   support

                    Direito Administrativo > Agentes públicos       0.62      0.50      0.56        20
                Direito Administrativo > Atos administrativos       0.50      0.40      0.44         5
   Direito Administrativo > Controle da administração pública       0.60      0.60      0.60         5
              Direito Administrativo > Licitações e contratos       0.60      0.60      0.60         5
          Direito Administrativo > Organização administrativa       0.57      0.80      0.67         5
             Direito Administrativo > Poderes administrativos       0.60      0.60      0.60         5
                   Direito Administrativo > Serviços públicos       0.50      0.75      0.60         4
Direito Constitucional > Defesa do Estado e segurança pública       0.81      0.81      0.81        27
   Direito Constitucional > Direitos e garantias fundamentais       0.60      0.50      0.55        18
                        Direito Constitucional > Ordem social       0.83      0.62      0.71         8
               Direito Constitucional > Organização do Estado       0.40      0.46      0.43        13
             Direito Constitucional > Organização dos poderes       0.65      0.70      0.68        37
        Direito Penal > Crimes contra a Administração Pública       0.60      0.75      0.67         4
                       Direito Penal > Crimes contra a pessoa       0.62      0.83      0.71         6
                   Direito Penal > Crimes contra o patrimônio       0.60      0.60      0.60         5
          Direito Penal > Princípios e aplicação da lei penal       1.00      1.00      1.00         4
                Direito Penal > Teoria do crime — fato típico       0.00      0.00      0.00         5

                                                     accuracy                           0.63       176
                                                    macro avg       0.60      0.62      0.60       176
                                                 weighted avg       0.63      0.63      0.63       176

Classes fora do treino (menos de 4 exemplos): Direito Administrativo > Improbidade administrativa, Direito Administrativo > Regime jurídico-administrativo e princípios, Direito Administrativo > Responsabilidade civil do Estado, Direito Constitucional > Teoria da Constituição e poder constituinte, Direito Penal > Crimes contra a fé pública, Direito Penal > Ilicitude, Direito Penal > Punibilidade

```
