"""Extração da taxonomia (conteúdo programático) a partir dos editais.

Os editais listam o conteúdo de cada disciplina como texto corrido com
numeração hierárquica ("1 Poder constituinte. 1.1 Fundamentos. 2 ..."). A
hierarquia é reconstruída com um portão sequencial: um número só é aceito
como novo tópico se for um sucessor plausível do tópico atual (próximo
irmão, primeiro filho, ou irmão de um ancestral). Isso evita que números
dentro do texto ("Lei nº 8.666/1993", "CF/88") virem tópicos falsos.

Uso: ``python -m src.classificacao.taxonomia`` gera
``config/taxonomias/{slug}.json`` para cada edital do manifesto.
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

from src.config import DIR_CONFIG, DIR_EDITAIS

CAMINHO_SECOES = DIR_CONFIG / "editais_secoes.json"
DIR_TAXONOMIAS = DIR_CONFIG / "taxonomias"

# Cabeçalho de disciplina: nome em CAIXA ALTA seguido de dois-pontos.
RE_DISCIPLINA = re.compile(
    r"(?:^|\.\s+|\n)\s*((?:NO[ÇC][ÕO]ES DE )?[A-ZÇÃÕÁÉÍÓÚÂÊÔÜ][A-ZÇÃÕÁÉÍÓÚÂÊÔÜ\d/() ,\-]{4,80}?):\s"
)
# Candidato a marcador de tópico: número hierárquico após fim de frase.
RE_MARCADOR = re.compile(r"(?:(?<=[.;:])\s+|^)(\d{1,2}(?:\.\d{1,2})*)\s+(?=\S)")


@dataclass
class Topico:
    """Um tópico do edital, com numeração original e filhos."""

    numero: str
    titulo: str = ""
    filhos: list["Topico"] = field(default_factory=list)

    def para_dict(self) -> dict:
        d = {"numero": self.numero, "titulo": self.titulo.strip(" .")}
        if self.filhos:
            d["filhos"] = [f.para_dict() for f in self.filhos]
        return d


def _tupla(numero: str) -> tuple[int, ...]:
    return tuple(int(p) for p in numero.split("."))


def _sucessor_plausivel(atual: tuple[int, ...], candidato: tuple[int, ...]) -> bool:
    """O candidato pode vir depois do tópico atual na numeração do edital?

    Aceita: primeiro filho (1 -> 1.1), próximo irmão (1.2 -> 1.3) e próximo
    irmão de qualquer ancestral (1.3.2 -> 2). Tolera UM pulo de numeração
    (erro comum de edital, ex.: PRF 2021 pula de 2 para 2.2).
    """
    if not atual:
        return candidato == (1,)
    # primeiro filho (tolerando pulo: .1 ou .2)
    if candidato[:-1] == atual and candidato[-1] in (1, 2):
        return True
    # próximo irmão de si ou de um ancestral (tolerando um pulo)
    for nivel in range(len(atual), 0, -1):
        prefixo = atual[:nivel]
        if len(candidato) == nivel and candidato[:-1] == prefixo[:-1]:
            if candidato[-1] in (prefixo[-1] + 1, prefixo[-1] + 2):
                return True
    return False


def parse_topicos(corpo: str) -> tuple[list[Topico], list[str]]:
    """Reconstrói a árvore de tópicos de uma disciplina a partir do texto corrido."""
    avisos: list[str] = []
    raiz: list[Topico] = []
    pilha: list[Topico] = []  # caminho até o tópico atual
    atual: tuple[int, ...] = ()
    pos = 0
    pendencias: list[tuple[tuple[int, ...], int, int]] = []

    for m in RE_MARCADOR.finditer(corpo):
        cand = _tupla(m.group(1))
        if not _sucessor_plausivel(atual, cand):
            continue
        pendencias.append((cand, m.start(1), m.end()))
        atual = cand

    for i, (numero, ini, fim) in enumerate(pendencias):
        fim_titulo = pendencias[i + 1][1] if i + 1 < len(pendencias) else len(corpo)
        titulo = corpo[fim:fim_titulo].strip()
        topico = Topico(numero=".".join(map(str, numero)), titulo=titulo)
        # posiciona na árvore
        while pilha and len(_tupla(pilha[-1].numero)) >= len(numero):
            pilha.pop()
        if pilha:
            pilha[-1].filhos.append(topico)
        else:
            raiz.append(topico)
        pilha.append(topico)

    if not raiz:
        avisos.append("nenhum tópico reconhecido")
    return raiz, avisos


def extrair_secao(caminho_pdf: Path, paginas: list[int], inicio: str, fim: str) -> str:
    """Extrai o texto da seção de conteúdo programático delimitada no config."""
    with pdfplumber.open(caminho_pdf) as pdf:
        texto = "\n".join(
            (p.extract_text() or "") for p in pdf.pages[paginas[0] - 1: paginas[1]]
        )
    m_ini = re.search(inicio, texto)
    if not m_ini:
        raise ValueError(f"{caminho_pdf.name}: marcador de início {inicio!r} não achado")
    texto = texto[m_ini.end():]
    m_fim = re.search(fim, texto)
    if m_fim:
        texto = texto[: m_fim.start()]
    # remove números de página soltos e quebras
    texto = re.sub(r"\n\d{1,3}\n", "\n", texto)
    return texto


def parse_disciplinas(texto: str) -> dict[str, list[Topico]]:
    """Divide a seção em disciplinas e parseia os tópicos de cada uma."""
    partes = RE_DISCIPLINA.split(texto)
    # partes = [preâmbulo, nome1, corpo1, nome2, corpo2, ...]
    resultado: dict[str, list[Topico]] = {}
    for i in range(1, len(partes) - 1, 2):
        nome = re.sub(r"\s+", " ", partes[i]).strip()
        corpo = partes[i + 1].replace("\n", " ")
        topicos, _ = parse_topicos(corpo)
        if topicos:
            resultado[nome] = topicos
    return resultado


def main() -> int:
    config = json.loads(CAMINHO_SECOES.read_text(encoding="utf-8"))
    DIR_TAXONOMIAS.mkdir(parents=True, exist_ok=True)
    for secao in config["secoes"]:
        slug = secao["slug"]
        pdf = DIR_EDITAIS / f"{slug}__edital_abertura.pdf"
        texto = extrair_secao(pdf, secao["paginas"], secao["inicio"], secao["fim"])
        disciplinas = parse_disciplinas(texto)
        saida = {
            "slug": slug,
            "cargo_referencia": secao["cargo_referencia"],
            "disciplinas": {
                nome: [t.para_dict() for t in tops] for nome, tops in disciplinas.items()
            },
        }
        destino = DIR_TAXONOMIAS / f"{slug}.json"
        destino.write_text(
            json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        resumo = ", ".join(f"{n} ({len(t)})" for n, t in disciplinas.items())
        print(f"{slug}: {len(disciplinas)} disciplinas -> {destino.name}")
        print(f"   {resumo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
