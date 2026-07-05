# Métricas do classificador local (Camada 2)

Gerado em 2026-07-05 00:01. Validação cruzada estratificada
sobre o conjunto de treino (rótulos da Camada 1 com confiança >= 0.75 +
revisões manuais). Reexecutar após cada rodada de revisão:
`python -m src.classificacao.modelo`.

## Modelo A — disciplina (todos os itens)

Previsões gravadas nesta execução: 0 (limiar 0.6).

```
                              precision    recall  f1-score   support

               Contabilidade       0.96      1.00      0.98        90
      Direito Administrativo       0.93      0.62      0.75        40
      Direito Constitucional       0.91      0.86      0.88       111
               Direito Penal       0.80      0.80      0.80        40
    Direito Processual Penal       0.70      0.84      0.76        25
            Direitos Humanos       1.00      1.00      1.00        18
                 Estatística       1.00      1.00      1.00        56
                      Física       1.00      0.93      0.96        27
                 Geopolítica       1.00      1.00      1.00         5
                 Informática       0.97      0.98      0.98       229
   Legislação Penal Especial       0.83      0.79      0.81        19
      Legislação de Trânsito       0.80      0.94      0.87        52
           Língua Portuguesa       0.99      1.00      1.00       182
Raciocínio Lógico-Matemático       1.00      0.97      0.98        86
    Ética no Serviço Público       0.78      1.00      0.88         7

                    accuracy                           0.94       987
                   macro avg       0.91      0.92      0.91       987
                weighted avg       0.94      0.94      0.94       987

```

## Modelo B — tópico fino (Direito Constitucional/Administrativo/Penal)

Previsões gravadas nesta execução: 0 (limiar 0.5).

**Limitação registrada**: o subtópico NÃO é previsto pelo modelo — com o
volume atual de treino, só o nível de tópico sustenta métrica decente.
Subtópicos vêm da Camada 1 (regras) e da revisão manual.

```
                                                               precision    recall  f1-score   support

                    Direito Administrativo > Agentes públicos       0.62      0.57      0.59        14
   Direito Administrativo > Controle da administração pública       0.50      0.75      0.60         4
          Direito Administrativo > Organização administrativa       0.67      0.80      0.73         5
                   Direito Administrativo > Serviços públicos       0.60      0.75      0.67         4
Direito Constitucional > Defesa do Estado e segurança pública       0.87      0.87      0.87        15
   Direito Constitucional > Direitos e garantias fundamentais       0.38      0.33      0.35         9
                        Direito Constitucional > Ordem social       1.00      0.67      0.80         6
               Direito Constitucional > Organização do Estado       0.50      0.50      0.50         8
             Direito Constitucional > Organização dos poderes       0.74      0.74      0.74        19

                                                     accuracy                           0.67        84
                                                    macro avg       0.65      0.66      0.65        84
                                                 weighted avg       0.68      0.67      0.67        84

Classes fora do treino (menos de 4 exemplos): Direito Administrativo > Atos administrativos, Direito Administrativo > Improbidade administrativa, Direito Administrativo > Licitações e contratos, Direito Administrativo > Poderes administrativos, Direito Administrativo > Responsabilidade civil do Estado, Direito Constitucional > Teoria da Constituição e poder constituinte, Direito Penal > Crimes contra a Administração Pública, Direito Penal > Crimes contra a fé pública, Direito Penal > Crimes contra a pessoa, Direito Penal > Crimes contra o patrimônio, Direito Penal > Ilicitude, Direito Penal > Princípios e aplicação da lei penal, Direito Penal > Punibilidade, Direito Penal > Teoria do crime — fato típico

```
