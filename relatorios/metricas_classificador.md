# Métricas do classificador local (Camada 2)

Gerado em 2026-07-05 08:49. Validação cruzada estratificada
sobre o conjunto de treino (rótulos da Camada 1 com confiança >= 0.75 +
revisões manuais). Reexecutar após cada rodada de revisão:
`python -m src.classificacao.modelo`.

## Modelo A — disciplina (todos os itens)

Previsões gravadas nesta execução: 2 (limiar 0.6).

```
                              precision    recall  f1-score   support

               Contabilidade       0.96      1.00      0.98       102
      Direito Administrativo       0.95      0.79      0.86        52
      Direito Constitucional       0.92      0.84      0.88       159
               Direito Penal       0.84      0.71      0.77        66
    Direito Processual Penal       0.80      0.91      0.85        53
            Direitos Humanos       0.94      1.00      0.97        29
                 Estatística       0.98      1.00      0.99        64
              Execução Penal       0.91      0.94      0.93        34
                      Física       1.00      0.85      0.92        27
                 Geopolítica       1.00      1.00      1.00         5
                 Informática       0.95      0.98      0.97       265
    Legislação Institucional       1.00      1.00      1.00         9
   Legislação Penal Especial       0.62      0.70      0.65        23
      Legislação de Trânsito       0.72      0.94      0.82        52
           Língua Portuguesa       0.99      0.98      0.98       220
Raciocínio Lógico-Matemático       1.00      0.95      0.97        99
    Ética no Serviço Público       0.78      1.00      0.88         7

                    accuracy                           0.93      1266
                   macro avg       0.90      0.92      0.91      1266
                weighted avg       0.93      0.93      0.93      1266

```

## Modelo B — tópico fino (Direito Constitucional/Administrativo/Penal)

Previsões gravadas nesta execução: 0 (limiar 0.5).

**Limitação registrada**: o subtópico NÃO é previsto pelo modelo — com o
volume atual de treino, só o nível de tópico sustenta métrica decente.
Subtópicos vêm da Camada 1 (regras) e da revisão manual.

```
                                                               precision    recall  f1-score   support

                    Direito Administrativo > Agentes públicos       0.59      0.53      0.56        19
                Direito Administrativo > Atos administrativos       0.67      0.50      0.57         4
   Direito Administrativo > Controle da administração pública       0.60      0.75      0.67         4
              Direito Administrativo > Licitações e contratos       0.60      0.60      0.60         5
          Direito Administrativo > Organização administrativa       0.50      0.80      0.62         5
             Direito Administrativo > Poderes administrativos       0.50      0.60      0.55         5
                   Direito Administrativo > Serviços públicos       0.40      0.50      0.44         4
Direito Constitucional > Defesa do Estado e segurança pública       0.80      0.87      0.83        23
   Direito Constitucional > Direitos e garantias fundamentais       0.50      0.28      0.36        18
                        Direito Constitucional > Ordem social       0.62      0.62      0.62         8
               Direito Constitucional > Organização do Estado       0.38      0.38      0.38        13
             Direito Constitucional > Organização dos poderes       0.68      0.72      0.70        32
        Direito Penal > Crimes contra a Administração Pública       0.75      0.75      0.75         4
                       Direito Penal > Crimes contra a pessoa       0.83      0.83      0.83         6
                   Direito Penal > Crimes contra o patrimônio       0.43      0.60      0.50         5
          Direito Penal > Princípios e aplicação da lei penal       1.00      1.00      1.00         4
                Direito Penal > Teoria do crime — fato típico       0.00      0.00      0.00         5

                                                     accuracy                           0.61       164
                                                    macro avg       0.58      0.61      0.59       164
                                                 weighted avg       0.60      0.61      0.60       164

Classes fora do treino (menos de 4 exemplos): Direito Administrativo > Improbidade administrativa, Direito Administrativo > Responsabilidade civil do Estado, Direito Constitucional > Teoria da Constituição e poder constituinte, Direito Penal > Crimes contra a fé pública, Direito Penal > Ilicitude, Direito Penal > Punibilidade

```
