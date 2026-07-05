"""Camada 2 da classificação: TF-IDF + classificador linear (100% local).

Dois modelos treinados com scikit-learn, sem nenhum serviço externo:

**Modelo A — disciplina**: treina nos itens cuja disciplina o mapeamento
estrutural já preencheu (`itens.disciplina IS NOT NULL`) e prevê a disciplina
dos itens restantes. Só grava previsões com probabilidade >= limiar; o resto
fica NULL e vai para a revisão manual.

**Modelo B — tópico (nível fino, disciplinas de Direito)**: treina nos
rótulos da Camada 1 com confiança alta (regras, >= 0.75) e nas revisões
manuais (metodo='manual'), e prevê o tópico dos demais itens de Direito.
Rótulo previsto = "disciplina > tópico". O SUBTÓPICO fica fora do modelo:
com ~220 exemplos de treino não há dados para o nível mais fino — limitação
registrada; subtópico vem das regras e da revisão manual.

Cada execução refaz o treino incluindo as revisões manuais acumuladas
(active learning simples: revisar -> retreinar -> revisar de novo).

Gera ``relatorios/metricas_classificador.md`` com validação cruzada
(precisão, revocação, F1 por classe) — o mapa de onde o modelo é confiável.

Uso: ``python -m src.classificacao.modelo``
"""
from __future__ import annotations

import sys
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline

from src.classificacao.regras import normalizar
from src.config import DIR_RELATORIOS
from src.db import conectar

LIMIAR_DISCIPLINA = 0.60  # abaixo disso a previsão não é gravada
LIMIAR_TOPICO = 0.50
MIN_EXEMPLOS_POR_CLASSE = 4  # classes mais raras que isso saem do treino
DISCIPLINAS_FINO = (
    "Direito Constitucional", "Direito Administrativo", "Direito Penal",
)


def montar_corpus(rows: list[tuple[int, str, str]]) -> tuple[list[int], list[str]]:
    """(id, texto, motivador) -> ids e documentos normalizados.

    O motivador entra uma vez e o texto do item duas: o item é o objeto da
    classificação, o motivador é contexto (mesma filosofia da Camada 1).
    """
    ids, docs = [], []
    for item_id, texto, motivador in rows:
        ids.append(item_id)
        docs.append(normalizar(f"{motivador} {texto} {texto}"))
    return ids, docs


def _pipeline() -> object:
    """TF-IDF (n-gramas 1-3) + regressão logística balanceada."""
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 3), min_df=2, sublinear_tf=True),
        LogisticRegression(max_iter=2000, class_weight="balanced", C=1.0),
    )


def _filtrar_classes_raras(ids, docs, rotulos) -> tuple[list, list, list, list[str]]:
    """Remove classes com menos exemplos que o mínimo (não dá para validar)."""
    from collections import Counter

    contagem = Counter(rotulos)
    excluidas = sorted(c for c, n in contagem.items() if n < MIN_EXEMPLOS_POR_CLASSE)
    manter = [i for i, r in enumerate(rotulos) if contagem[r] >= MIN_EXEMPLOS_POR_CLASSE]
    return ([ids[i] for i in manter], [docs[i] for i in manter],
            [rotulos[i] for i in manter], excluidas)


def _validar(docs: list[str], rotulos: list[str]) -> str:
    """Validação cruzada estratificada; devolve o relatório por classe."""
    n_folds = min(5, min(rotulos.count(r) for r in set(rotulos)))
    if n_folds < 2:
        return "(classes com poucos exemplos demais para validação cruzada)"
    cv = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    previsto = cross_val_predict(_pipeline(), docs, rotulos, cv=cv)
    return classification_report(rotulos, previsto, zero_division=0, digits=2)


def treinar_e_prever_disciplina(con) -> tuple[str, int]:
    """Modelo A: preenche itens.disciplina dos itens sem rótulo estrutural."""
    treino = con.execute(
        "SELECT i.id, i.texto, COALESCE(m.texto,''), i.disciplina FROM itens i "
        "LEFT JOIN textos_motivadores m ON m.id = i.texto_motivador_id "
        "WHERE i.disciplina IS NOT NULL"
    ).fetchall()
    alvo = con.execute(
        "SELECT i.id, i.texto, COALESCE(m.texto,'') FROM itens i "
        "LEFT JOIN textos_motivadores m ON m.id = i.texto_motivador_id "
        "WHERE i.disciplina IS NULL"
    ).fetchall()

    ids_t, docs_t = montar_corpus([(r[0], r[1], r[2]) for r in treino])
    rotulos_t = [r[3] for r in treino]
    ids_t, docs_t, rotulos_t, excluidas = _filtrar_classes_raras(ids_t, docs_t, rotulos_t)

    relatorio = _validar(docs_t, rotulos_t)
    if excluidas:
        relatorio += f"\nClasses fora do treino (menos de {MIN_EXEMPLOS_POR_CLASSE} exemplos): {', '.join(excluidas)}\n"

    gravados = 0
    if alvo:
        modelo = _pipeline().fit(docs_t, rotulos_t)
        ids_a, docs_a = montar_corpus(alvo)
        probas = modelo.predict_proba(docs_a)
        classes = modelo.classes_
        for item_id, p in zip(ids_a, probas):
            melhor = p.argmax()
            if p[melhor] >= LIMIAR_DISCIPLINA:
                con.execute(
                    "UPDATE itens SET disciplina = ? WHERE id = ?",
                    (classes[melhor], item_id),
                )
                gravados += 1
        con.commit()
    return relatorio, gravados


def treinar_e_prever_topico(con) -> tuple[str, int]:
    """Modelo B: tópico fino para itens das disciplinas de Direito do piloto."""
    marcadores = ", ".join("?" for _ in DISCIPLINAS_FINO)
    treino = con.execute(
        f"""
        SELECT i.id, i.texto, COALESCE(m.texto,''), c.topico
        FROM classificacoes c
        JOIN itens i ON i.id = c.item_id
        LEFT JOIN textos_motivadores m ON m.id = i.texto_motivador_id
        WHERE (c.metodo = 'manual')
           OR (c.metodo = 'regras' AND c.confianca >= 0.75)
        GROUP BY i.id HAVING c.metodo = MAX(c.metodo)  -- manual prevalece
        """
    ).fetchall()
    alvo = con.execute(
        f"""
        SELECT i.id, i.texto, COALESCE(m.texto,'')
        FROM itens i
        LEFT JOIN textos_motivadores m ON m.id = i.texto_motivador_id
        WHERE i.disciplina IN ({marcadores})
          AND i.id NOT IN (SELECT item_id FROM classificacoes
                           WHERE metodo = 'manual'
                              OR (metodo = 'regras' AND confianca >= 0.75))
        """,
        DISCIPLINAS_FINO,
    ).fetchall()

    ids_t, docs_t = montar_corpus([(r[0], r[1], r[2]) for r in treino])
    rotulos_t = [r[3] for r in treino]
    ids_t, docs_t, rotulos_t, excluidas = _filtrar_classes_raras(ids_t, docs_t, rotulos_t)

    relatorio = _validar(docs_t, rotulos_t)
    if excluidas:
        relatorio += f"\nClasses fora do treino (menos de {MIN_EXEMPLOS_POR_CLASSE} exemplos): {', '.join(excluidas)}\n"

    gravados = 0
    if alvo and len(set(rotulos_t)) >= 2:
        modelo = _pipeline().fit(docs_t, rotulos_t)
        ids_a, docs_a = montar_corpus(alvo)
        probas = modelo.predict_proba(docs_a)
        classes = modelo.classes_
        con.execute("DELETE FROM classificacoes WHERE metodo = 'modelo'")
        for item_id, p in zip(ids_a, probas):
            melhor = p.argmax()
            if p[melhor] >= LIMIAR_TOPICO:
                con.execute(
                    "INSERT INTO classificacoes (item_id, metodo, topico, confianca) "
                    "VALUES (?, 'modelo', ?, ?) "
                    "ON CONFLICT(item_id, metodo) DO UPDATE SET "
                    "topico=excluded.topico, confianca=excluded.confianca",
                    (item_id, classes[melhor], round(float(p[melhor]), 3)),
                )
                gravados += 1
        con.commit()
    return relatorio, gravados


def main() -> int:
    con = conectar()
    print("Modelo A (disciplina dos itens sem rótulo estrutural)...")
    rel_a, n_a = treinar_e_prever_disciplina(con)
    print(f"  {n_a} itens receberam disciplina do modelo")
    print("Modelo B (tópico fino nas disciplinas de Direito)...")
    rel_b, n_b = treinar_e_prever_topico(con)
    print(f"  {n_b} itens receberam tópico do modelo")

    DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho = DIR_RELATORIOS / "metricas_classificador.md"
    caminho.write_text(
        f"""# Métricas do classificador local (Camada 2)

Gerado em {datetime.now():%Y-%m-%d %H:%M}. Validação cruzada estratificada
sobre o conjunto de treino (rótulos da Camada 1 com confiança >= 0.75 +
revisões manuais). Reexecutar após cada rodada de revisão:
`python -m src.classificacao.modelo`.

## Modelo A — disciplina (todos os itens)

Previsões gravadas nesta execução: {n_a} (limiar {LIMIAR_DISCIPLINA}).

```
{rel_a}
```

## Modelo B — tópico fino (Direito Constitucional/Administrativo/Penal)

Previsões gravadas nesta execução: {n_b} (limiar {LIMIAR_TOPICO}).

**Limitação registrada**: o subtópico NÃO é previsto pelo modelo — com o
volume atual de treino, só o nível de tópico sustenta métrica decente.
Subtópicos vêm da Camada 1 (regras) e da revisão manual.

```
{rel_b}
```
""",
        encoding="utf-8",
    )
    print(f"\nMétricas: {caminho}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
