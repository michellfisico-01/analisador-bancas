"""Classificador baseline por regras e palavras-chave (sem API).

Cada subtópico da taxonomia consolidada traz âncoras: palavras-chave e
referências legais (ex.: "art. 5º", "lei nº 8.112", "habeas corpus"). O
classificador pontua o item (texto + texto motivador) por âncora encontrada,
com peso maior para referências legais explícitas, que são pistas fortes e
baratas. Devolve o subtópico de maior pontuação e uma confiança interpretável.

Esta é a Camada 1 da classificação (Fase 2). Itens sem nenhuma âncora ficam
sem classificação por regras — vão para a Camada 2 (modelo local) e(ou)
para a revisão manual.

Uso: ``python -m src.classificacao.regras`` classifica todos os itens do
banco e grava em ``classificacoes`` com ``metodo='regras'``.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from src.config import DIR_CONFIG
from src.db import conectar

CAMINHO_TAXONOMIA = DIR_CONFIG / "taxonomias" / "consolidada.json"

PESO_REFERENCIA_LEGAL = 2.0  # âncora com "art." ou "lei " pesa mais
PESO_PALAVRA_CHAVE = 1.0


@dataclass(frozen=True)
class Ancora:
    """Uma âncora compilada: padrão com fronteiras de palavra, peso e rótulo."""

    padrao: "re.Pattern[str]"
    peso: float
    rotulo: str  # texto original normalizado (para exibir na revisão)


@dataclass(frozen=True)
class Alvo:
    """Um subtópico classificável, com suas âncoras já compiladas."""

    disciplina: str
    topico: str
    subtopico: str
    ancoras: tuple[Ancora, ...]


@dataclass
class Resultado:
    disciplina: str
    topico: str
    subtopico: str
    confianca: float
    ancoras_casadas: list[str]


def normalizar(texto: str) -> str:
    """Minúsculas, sem acentos, espaços colapsados — para casar âncoras."""
    sem_acento = (
        unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"\s+", " ", sem_acento.lower())


def _peso(ancora: str) -> float:
    """Âncoras mais específicas pesam mais.

    Referências legais ("art. 144", "lei nº 8.112") e frases de várias
    palavras ("habeas corpus", "responsabilidade civil do estado") são
    pistas muito menos ambíguas que uma palavra isolada ("pena", "servidor"),
    que sozinha vaza para itens de outras disciplinas. O peso maior faz o
    subtópico certo vencer o empate e eleva a confiança dos casos confiáveis.
    """
    tem_ref_legal = bool(re.search(r"\bart\b|\blei\b|\bartigo\b", ancora))
    e_frase = " " in ancora.strip()
    return PESO_REFERENCIA_LEGAL if (tem_ref_legal or e_frase) else PESO_PALAVRA_CHAVE


def _compilar(ancora_norm: str) -> "re.Pattern[str]":
    """Compila a âncora com fronteiras de palavra e espaço flexível.

    Usa lookarounds em vez de \\b porque âncoras podem terminar em dígito
    ("art. 5") — assim "art. 5" não casa dentro de "art. 51" — e conter
    pontuação. Espaços viram \\s+ para tolerar quebras de linha do PDF.
    """
    partes = [re.escape(tok) for tok in ancora_norm.split(" ")]
    corpo = r"\s+".join(partes)
    return re.compile(rf"(?<![a-z0-9]){corpo}(?![a-z0-9])")


def carregar_alvos(caminho: Path = CAMINHO_TAXONOMIA) -> list[Alvo]:
    """Achata a taxonomia consolidada na lista de subtópicos classificáveis."""
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    alvos: list[Alvo] = []
    for disc in dados["disciplinas_fino"]:
        for topico in disc["topicos"]:
            for sub in topico["subtopicos"]:
                ancoras = tuple(
                    Ancora(padrao=_compilar(n), peso=_peso(n), rotulo=n)
                    for n in (normalizar(a) for a in sub["ancoras"])
                )
                alvos.append(
                    Alvo(
                        disciplina=disc["disciplina"],
                        topico=topico["topico"],
                        subtopico=sub["nome"],
                        ancoras=ancoras,
                    )
                )
    return alvos


def _confianca(score: float) -> float:
    """Mapeia pontuação acumulada para [0,1) de forma monotônica e interpretável.

    score 1 -> 0.50, score 2 -> 0.75, score 3 -> 0.875... (1 - 0.5^score).
    Reflete: quanto mais âncoras (e mais fortes) casam, maior a confiança.
    """
    return 1.0 - 0.5**score


def classificar(texto_item: str, texto_motivador: str, alvos: list[Alvo]) -> Resultado | None:
    """Classifica um item. Devolve o melhor subtópico ou None se nada casar."""
    # o item é o objeto da classificação; o motivador é só contexto —
    # âncora casada apenas no motivador vale metade do peso
    texto_norm = normalizar(texto_item)
    motivador_norm = normalizar(texto_motivador)
    melhor: Resultado | None = None
    melhor_score = 0.0
    for alvo in alvos:
        score = 0.0
        casadas: list[str] = []
        for ancora in alvo.ancoras:
            if ancora.padrao.search(texto_norm):
                score += ancora.peso
                casadas.append(ancora.rotulo)
            elif ancora.padrao.search(motivador_norm):
                score += ancora.peso * 0.5
                casadas.append(f"{ancora.rotulo} (motivador)")
        if score > melhor_score:
            melhor_score = score
            melhor = Resultado(
                disciplina=alvo.disciplina,
                topico=alvo.topico,
                subtopico=alvo.subtopico,
                confianca=round(_confianca(score), 3),
                ancoras_casadas=casadas,
            )
    return melhor


def classificar_banco() -> dict[str, int]:
    """Classifica todos os itens do banco por regras. Devolve contagens."""
    alvos = carregar_alvos()
    con = conectar()
    cur = con.cursor()
    itens = cur.execute(
        "SELECT i.id, i.texto, COALESCE(m.texto, '') "
        "FROM itens i LEFT JOIN textos_motivadores m ON m.id = i.texto_motivador_id"
    ).fetchall()

    cur.execute("DELETE FROM classificacoes WHERE metodo = 'regras'")
    contagem = {"classificados": 0, "sem_classe": 0, "baixa_confianca": 0}
    for item_id, texto, motivador in itens:
        r = classificar(texto, motivador or "", alvos)
        if r is None:
            contagem["sem_classe"] += 1
            continue
        cur.execute(
            "INSERT INTO classificacoes (item_id, metodo, topico, subtopico, confianca) "
            "VALUES (?, 'regras', ?, ?, ?)",
            (item_id, f"{r.disciplina} > {r.topico}", r.subtopico, r.confianca),
        )
        contagem["classificados"] += 1
        if r.confianca < 0.75:
            contagem["baixa_confianca"] += 1
    con.commit()
    return contagem


def main() -> int:
    print("Classificando itens por regras (baseline, sem API)...")
    c = classificar_banco()
    total = c["classificados"] + c["sem_classe"]
    print(f"  {c['classificados']}/{total} itens receberam classificação por regras")
    print(f"  {c['sem_classe']} sem âncora (vão para o modelo local/revisão manual)")
    print(f"  {c['baixa_confianca']} classificados com baixa confiança (< 0.75)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
