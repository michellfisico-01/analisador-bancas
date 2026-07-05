"""Preenchimento de disciplina pela ordem do edital (inferência estrutural).

Os cadernos CEBRASPE apresentam as disciplinas na mesma ordem em que o
edital lista o conteúdo programático. Isso restringe fortemente o que um
trecho sem rótulo pode ser: um buraco entre "Língua Portuguesa" e
"Informática" só pode conter as disciplinas que ficam ENTRE as duas na
ordem do edital (ex.: Raciocínio Lógico) — ou ser continuação das vizinhas.

Salvaguardas conservadoras:
- se os vizinhos do buraco violam a ordem do edital (indício de rótulo
  errado), o buraco NÃO é preenchido;
- com um único candidato possível, o preenchimento é direto (estrutural);
- com vários candidatos, decide o modelo da Camada 2 RESTRITO a esses
  candidatos, bloco a bloco, com limiar sobre a probabilidade renormalizada
  — escolher entre 2-3 opções é muito mais confiável que entre 15;
- o que não passar no limiar continua NULL (fila de revisão).

Uso: ``python -m src.classificacao.ordem_edital``
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict

from src.classificacao.disciplinas import MAPA_EDITAL_CANONICO
from src.classificacao.modelo import _pipeline, montar_corpus
from src.classificacao.taxonomia import DIR_TAXONOMIAS
from src.db import conectar

LIMIAR_RESTRITO = 0.55  # sobre a probabilidade renormalizada aos candidatos


def ordem_disciplinas(slug: str) -> list[str]:
    """Disciplinas canônicas na ordem em que o edital as apresenta."""
    dados = json.loads((DIR_TAXONOMIAS / f"{slug}.json").read_text(encoding="utf-8"))
    ordem: list[str] = []
    for nome_edital in dados["disciplinas"]:
        nome_upper = nome_edital.upper()
        for chave, canonicas in MAPA_EDITAL_CANONICO:
            if chave in nome_upper:
                for c in canonicas:
                    if c not in ordem:
                        ordem.append(c)
                break
    return ordem


def candidatos_do_buraco(
    ordem: list[str], vizinho_esq: str | None, vizinho_dir: str | None
) -> list[str]:
    """Disciplinas possíveis para um buraco, dados os vizinhos rotulados.

    Devolve lista vazia quando a ordem observada contradiz a do edital
    (sinal de rótulo errado num vizinho — melhor não inferir nada).
    """
    if vizinho_esq is not None and vizinho_esq not in ordem:
        return []
    if vizinho_dir is not None and vizinho_dir not in ordem:
        return []
    if vizinho_esq is not None and vizinho_dir is not None:
        i, j = ordem.index(vizinho_esq), ordem.index(vizinho_dir)
        if i > j:
            return []  # vizinhos fora de ordem: não inferir
        return ordem[i: j + 1]
    if vizinho_esq is not None:
        return ordem[ordem.index(vizinho_esq):]
    if vizinho_dir is not None:
        return ordem[: ordem.index(vizinho_dir) + 1]
    return []


def preencher(con) -> dict[str, int]:
    """Preenche buracos de disciplina prova a prova. Devolve contagens."""
    # modelo da Camada 2 treinado em tudo que já tem rótulo
    treino = con.execute(
        "SELECT i.id, i.texto, COALESCE(m.texto,''), i.disciplina FROM itens i "
        "LEFT JOIN textos_motivadores m ON m.id = i.texto_motivador_id "
        "WHERE i.disciplina IS NOT NULL"
    ).fetchall()
    _, docs_t = montar_corpus([(r[0], r[1], r[2]) for r in treino])
    modelo = _pipeline().fit(docs_t, [r[3] for r in treino])
    classes = list(modelo.classes_)

    provas = con.execute(
        "SELECT p.id, c.slug FROM provas p JOIN concursos c ON c.id = p.concurso_id"
    ).fetchall()

    contagem = {"estrutural": 0, "modelo_restrito": 0, "sem_decisao": 0,
                "ordem_violada": 0}
    for prova_id, slug in provas:
        ordem = ordem_disciplinas(slug)
        linhas = con.execute(
            "SELECT i.id, i.numero, i.disciplina, i.texto_motivador_id, "
            "i.texto, COALESCE(m.texto,'') "
            "FROM itens i LEFT JOIN textos_motivadores m ON m.id = i.texto_motivador_id "
            "WHERE i.prova_id = ? ORDER BY i.numero", (prova_id,),
        ).fetchall()

        pos = 0
        n = len(linhas)
        while pos < n:
            if linhas[pos][2] is not None:
                pos += 1
                continue
            fim = pos
            while fim < n and linhas[fim][2] is None:
                fim += 1
            esq = linhas[pos - 1][2] if pos > 0 else None
            dir_ = linhas[fim][2] if fim < n else None
            cands = candidatos_do_buraco(ordem, esq, dir_)
            buraco = linhas[pos:fim]

            if not cands:
                contagem["ordem_violada" if (esq and dir_) else "sem_decisao"] += len(buraco)
            elif len(cands) == 1:
                con.executemany(
                    "UPDATE itens SET disciplina = ? WHERE id = ?",
                    [(cands[0], l[0]) for l in buraco],
                )
                contagem["estrutural"] += len(buraco)
            else:
                # decide o modelo, restrito aos candidatos, por bloco
                idx_cands = [classes.index(c) for c in cands if c in classes]
                if not idx_cands:
                    contagem["sem_decisao"] += len(buraco)
                    pos = fim
                    continue
                blocos: dict = defaultdict(list)
                for l in buraco:
                    blocos[l[3] if l[3] is not None else f"solo{l[0]}"].append(l)
                for grupo in blocos.values():
                    _, docs = montar_corpus([(l[0], l[4], l[5]) for l in grupo])
                    probas = modelo.predict_proba(docs).mean(axis=0)
                    restrito = probas[idx_cands]
                    restrito = restrito / restrito.sum()
                    melhor = restrito.argmax()
                    if restrito[melhor] >= LIMIAR_RESTRITO:
                        escolhida = classes[idx_cands[melhor]]
                        con.executemany(
                            "UPDATE itens SET disciplina = ? WHERE id = ?",
                            [(escolhida, l[0]) for l in grupo],
                        )
                        contagem["modelo_restrito"] += len(grupo)
                    else:
                        contagem["sem_decisao"] += len(grupo)
            pos = fim
    con.commit()
    return contagem


def main() -> int:
    con = conectar()
    c = preencher(con)
    print(f"Preenchidos pela estrutura do edital (candidato único): {c['estrutural']}")
    print(f"Preenchidos pelo modelo restrito aos candidatos:        {c['modelo_restrito']}")
    print(f"Sem decisão (continuam NULL, fila de revisão):          {c['sem_decisao']}")
    print(f"Vizinhos violam a ordem do edital (não inferido):       {c['ordem_violada']}")
    restam, total = con.execute(
        "SELECT SUM(CASE WHEN disciplina IS NULL THEN 1 ELSE 0 END), COUNT(*) "
        "FROM itens"
    ).fetchone()
    print(f"\nItens ainda sem disciplina: {restam}/{total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
