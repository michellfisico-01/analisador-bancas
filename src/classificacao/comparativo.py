"""Relatório comparativo das abordagens de classificação (regras x modelo).

Gera ``relatorios/comparativo_classificacao.md`` com:
- cobertura de cada método (quantos itens cada um classificou);
- concordância entre regras (Camada 1) e modelo local (Camada 2) no tópico;
- tamanho da fila de revisão manual;
- distribuição de confiança por método.

Pode rodar a qualquer momento: seções sem dados dizem isso explicitamente.

Uso: ``python -m src.classificacao.comparativo``
"""
from __future__ import annotations

import sys
from datetime import datetime

from src.classificacao.revisao import candidatos
from src.config import DIR_RELATORIOS
from src.db import conectar


def gerar(con) -> str:
    total_itens, = con.execute("SELECT COUNT(*) FROM itens").fetchone()
    linhas = [
        "# Comparativo das abordagens de classificação",
        "",
        f"Gerado em {datetime.now():%Y-%m-%d %H:%M}. Total de itens: {total_itens}.",
        "",
        "## Cobertura por método",
        "",
        "| Método | Itens classificados | Confiança média | Baixa confiança (<0.75) |",
        "|---|---:|---:|---:|",
    ]
    for metodo in ("regras", "modelo", "manual"):
        n, conf_media, baixa = con.execute(
            "SELECT COUNT(*), ROUND(AVG(confianca), 3), "
            "SUM(CASE WHEN confianca < 0.75 THEN 1 ELSE 0 END) "
            "FROM classificacoes WHERE metodo = ?",
            (metodo,),
        ).fetchone()
        linhas.append(f"| {metodo} | {n} | {conf_media or '—'} | {baixa or 0} |")

    n_modelo, = con.execute(
        "SELECT COUNT(*) FROM classificacoes WHERE metodo='modelo'"
    ).fetchone()

    linhas += ["", "## Concordância regras x modelo (Camada 1 x Camada 2)", ""]
    if n_modelo == 0:
        linhas.append(
            "_O modelo local ainda não foi treinado — rode "
            "`python -m src.classificacao.modelo` para preencher esta seção._"
        )
    else:
        ambos, topico_igual = con.execute(
            """
            SELECT COUNT(*),
                   SUM(CASE WHEN r.topico = mo.topico THEN 1 ELSE 0 END)
            FROM classificacoes r
            JOIN classificacoes mo ON mo.item_id = r.item_id AND mo.metodo = 'modelo'
            WHERE r.metodo = 'regras'
            """
        ).fetchone()
        if ambos:
            linhas += [
                f"- Itens classificados pelos dois métodos: **{ambos}**",
                f"- Concordância em disciplina/tópico: **{topico_igual}/{ambos}** "
                f"({100 * topico_igual / ambos:.1f}%)",
                "- (subtópico não é previsto pelo modelo — limitação registrada "
                "em `relatorios/metricas_classificador.md`)",
            ]
        else:
            linhas.append(
                "_Sem interseção: o modelo só prevê itens que as regras não "
                "resolveram com confiança alta (por construção)._"
            )

    fila = len(candidatos(con))
    linhas += [
        "",
        "## Fila de revisão manual",
        "",
        f"- Itens aguardando revisão humana: **{fila}** "
        "(divergências entre métodos e confianças < 0.75)",
        "- Abrir a revisão: `python -m src.classificacao.revisao`",
        "",
        "## Disciplina dos itens (mapeamento estrutural)",
        "",
        "| Disciplina | Itens |",
        "|---|---:|",
    ]
    for disc, n in con.execute(
        "SELECT COALESCE(disciplina, '(sem disciplina — fila de revisão)'), COUNT(*) "
        "FROM itens GROUP BY disciplina ORDER BY COUNT(*) DESC"
    ).fetchall():
        linhas.append(f"| {disc} | {n} |")
    return "\n".join(linhas) + "\n"


def main() -> int:
    con = conectar()
    DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho = DIR_RELATORIOS / "comparativo_classificacao.md"
    caminho.write_text(gerar(con), encoding="utf-8")
    print(f"Relatório: {caminho}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
