"""Base comum da análise (Fase 3): consulta canônica dos itens rotulados.

Define a REGRA DE PRECEDÊNCIA dos rótulos finos, usada em toda a análise:
``manual`` (revisão humana) > ``regras`` com confiança >= 0.75 > ``modelo``
> ``regras`` com confiança baixa. A origem do rótulo escolhido acompanha
cada linha, para que os relatórios possam declarar a cobertura por fonte.
"""
from __future__ import annotations

import pandas as pd

from src.db import conectar

# disciplina piloto -> analisada no nível fino
DISCIPLINAS_PILOTO = (
    "Direito Constitucional", "Direito Administrativo", "Direito Penal",
)

SQL_ITENS = """
SELECT i.id            AS item_id,
       c.banca         AS banca,
       c.orgao         AS orgao,
       c.nome          AS concurso,
       c.ano_prova     AS ano,
       p.cargo         AS cargo,
       i.numero        AS numero,
       i.disciplina    AS disciplina,
       i.gabarito      AS gabarito,
       i.status        AS status,
       i.texto         AS texto
FROM itens i
JOIN provas p    ON p.id = i.prova_id
JOIN concursos c ON c.id = p.concurso_id
"""

SQL_CLASSIFICACOES = """
SELECT item_id, metodo, topico, subtopico, confianca
FROM classificacoes
"""


def carregar_itens() -> pd.DataFrame:
    """Itens com metadados do concurso e o melhor rótulo fino disponível.

    Colunas adicionais: ``topico``, ``subtopico``, ``origem_rotulo``
    (manual|regras_alta|modelo|regras_baixa|NULL).
    """
    con = conectar()
    itens = pd.read_sql_query(SQL_ITENS, con)
    cls = pd.read_sql_query(SQL_CLASSIFICACOES, con)

    def prioridade(linha) -> int:
        if linha.metodo == "manual":
            return 0
        if linha.metodo == "regras" and (linha.confianca or 0) >= 0.75:
            return 1
        if linha.metodo == "modelo":
            return 2
        return 3

    if not cls.empty:
        cls = cls.assign(prioridade=cls.apply(prioridade, axis=1))
        cls = cls.sort_values(["item_id", "prioridade"]).groupby("item_id").first()
        origem = cls.prioridade.map(
            {0: "manual", 1: "regras_alta", 2: "modelo", 3: "regras_baixa"}
        )
        cls = cls.assign(origem_rotulo=origem)[["topico", "subtopico", "origem_rotulo"]]
        itens = itens.merge(cls, left_on="item_id", right_index=True, how="left")
    else:
        itens[["topico", "subtopico", "origem_rotulo"]] = None

    # nos rótulos finos, "Disciplina > Tópico" — separa só o tópico
    com_topico = itens.topico.notna()
    itens.loc[com_topico, "topico"] = (
        itens.loc[com_topico, "topico"].str.split(" > ").str[-1]
    )
    return itens
