"""Fluxo de revisão manual das classificações.

Seleciona os itens que precisam de juízo humano — regra do projeto: dúvida
jurídica fina nunca é decidida pela máquina — e apresenta um a um no
terminal. São candidatos à revisão:

1. itens em que regras (Camada 1) e modelo (Camada 2) DIVERGEM no tópico;
2. itens com confiança baixa (< 0.75) em qualquer método;
3. itens sem nenhuma classificação.

Cada correção realimenta o treino da Camada 2: depois de uma rodada de
revisão, rode ``python -m src.classificacao.modelo`` para retreinar.

A decisão do revisor é gravada com ``metodo='manual'`` e ``revisado=1`` —
na análise (Fase 3), a classificação manual sempre prevalece.

Uso: ``python -m src.classificacao.revisao [--listar]``
"""
from __future__ import annotations

import argparse
import sys
import textwrap

from src.db import conectar

LIMIAR_CONFIANCA = 0.75

SQL_CANDIDATOS = """
WITH r AS (SELECT item_id, topico, subtopico, confianca
           FROM classificacoes WHERE metodo = 'regras'),
     mo AS (SELECT item_id, topico, subtopico, confianca
            FROM classificacoes WHERE metodo = 'modelo'),
     m AS (SELECT item_id FROM classificacoes WHERE metodo = 'manual')
SELECT i.id, i.numero, c.nome, p.cargo, i.texto,
       COALESCE(tm.texto, '') AS motivador,
       r.topico, r.subtopico, r.confianca,
       mo.topico, mo.subtopico, mo.confianca
FROM itens i
JOIN provas p     ON p.id = i.prova_id
JOIN concursos c  ON c.id = p.concurso_id
LEFT JOIN textos_motivadores tm ON tm.id = i.texto_motivador_id
LEFT JOIN r ON r.item_id = i.id
LEFT JOIN mo ON mo.item_id = i.id
WHERE i.id NOT IN (SELECT item_id FROM m)
  AND (
        -- divergência entre métodos (quando ambos existem)
        (r.topico IS NOT NULL AND mo.topico IS NOT NULL AND r.topico <> mo.topico)
        -- baixa confiança em qualquer método existente
        OR (r.confianca IS NOT NULL AND r.confianca < :limiar)
        OR (mo.confianca IS NOT NULL AND mo.confianca < :limiar)
      )
ORDER BY c.nome, i.numero
"""


def candidatos(con) -> list[tuple]:
    return con.execute(SQL_CANDIDATOS, {"limiar": LIMIAR_CONFIANCA}).fetchall()


def _mostrar(item: tuple) -> None:
    (item_id, numero, concurso, cargo, texto, motivador,
     r_top, r_sub, r_conf, mo_top, mo_sub, mo_conf) = item
    print("\n" + "=" * 78)
    print(f"[{concurso} | {cargo} | item {numero}]  (id interno {item_id})")
    if motivador:
        print("\nTEXTO MOTIVADOR:")
        print(textwrap.fill(motivador[:600], width=78))
    print("\nITEM:")
    print(textwrap.fill(texto, width=78))
    print(f"\n  1) regras: {r_top or '—'} > {r_sub or '—'}  (conf. {r_conf})")
    print(f"  2) modelo: {mo_top or '—'} > {mo_sub or '—'}  (conf. {mo_conf})")


def revisar(con) -> None:
    fila = candidatos(con)
    if not fila:
        print("Nenhum item pendente de revisão manual.")
        return
    print(f"{len(fila)} itens na fila de revisão.")
    print("Comandos: 1=aceitar regras | 2=aceitar modelo | d=digitar | p=pular | q=sair")
    for item in fila:
        _mostrar(item)
        escolha = input("\n> ").strip().lower()
        if escolha == "q":
            break
        if escolha == "p" or escolha == "":
            continue
        if escolha == "1":
            topico, subtopico = item[6], item[7]
        elif escolha == "2":
            topico, subtopico = item[9], item[10]
        elif escolha == "d":
            topico = input("  disciplina > tópico: ").strip()
            subtopico = input("  subtópico (vazio = nenhum): ").strip() or None
        else:
            print("  comando desconhecido, pulando")
            continue
        if not topico:
            print("  classificação vazia, pulando")
            continue
        con.execute(
            "INSERT INTO classificacoes (item_id, metodo, topico, subtopico, "
            "confianca, revisado) VALUES (?, 'manual', ?, ?, 1.0, 1) "
            "ON CONFLICT(item_id, metodo) DO UPDATE SET topico=excluded.topico, "
            "subtopico=excluded.subtopico, revisado=1",
            (item[0], topico, subtopico),
        )
        con.commit()
        print("  gravado.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Revisão manual de classificações")
    parser.add_argument("--listar", action="store_true",
                        help="só lista a fila, sem abrir a revisão interativa")
    args = parser.parse_args()
    con = conectar()
    if args.listar:
        fila = candidatos(con)
        print(f"{len(fila)} itens na fila de revisão manual.")
        for item in fila[:30]:
            print(f"  {item[2]:22s} item {item[1]:3d}  "
                  f"regras={item[6] or '—'}  modelo={item[9] or '—'}")
        if len(fila) > 30:
            print(f"  ... e mais {len(fila) - 30}")
        return 0
    revisar(con)
    return 0


if __name__ == "__main__":
    sys.exit(main())
