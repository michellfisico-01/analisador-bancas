"""Extração de gabaritos definitivos da FGV (múltipla escolha).

Formato observado (TRF1 2024): um único PDF com uma seção por cargo/tipo,
com cabeçalho "``<cargo> - TIPO <n>``" seguido de pares de linhas
número/letra (20 colunas por par). ``*`` marca questão anulada — convertida
para ``X``, a mesma convenção do pipeline CEBRASPE.
"""
from __future__ import annotations

import re
from pathlib import Path

import pdfplumber

RESPOSTAS_VALIDAS = set("ABCDE")


def extrair_gabarito_fgv(caminho_pdf: Path, secao: str) -> dict[int, str]:
    """Lê o gabarito da seção ``secao`` (ex.: "Analista ... - TIPO 1").

    Devolve {numero: 'A'..'E' | 'X'}. Lança ValueError se a seção não for
    encontrada ou o padrão quebrar — dado ruim estoura cedo.
    """
    alvo = re.sub(r"\s+", " ", secao).strip().lower()
    with pdfplumber.open(caminho_pdf) as pdf:
        linhas: list[str] = []
        for pagina in pdf.pages:
            linhas.extend((pagina.extract_text() or "").splitlines())

    gabarito: dict[int, str] = {}
    dentro = False
    numeros_pendentes: list[int] | None = None
    for linha in linhas:
        normalizada = re.sub(r"\s+", " ", linha).strip().lower()
        if " - tipo " in normalizada or normalizada.endswith(("tipo 1", "tipo 2",
                                                              "tipo 3", "tipo 4")):
            if dentro:
                break  # começou a próxima seção: terminamos
            dentro = normalizada == alvo
            continue
        if not dentro:
            continue
        tokens = linha.split()
        if not tokens:
            continue
        if all(t.isdigit() for t in tokens):
            numeros_pendentes = [int(t) for t in tokens]
        elif numeros_pendentes and all(
            t in RESPOSTAS_VALIDAS or t == "*" for t in tokens
        ):
            for numero, resposta in zip(numeros_pendentes, tokens):
                if numero in gabarito:
                    raise ValueError(
                        f"{caminho_pdf.name}: questão {numero} duplicada em {secao!r}"
                    )
                gabarito[numero] = "X" if resposta == "*" else resposta
            numeros_pendentes = None

    if not gabarito:
        raise ValueError(
            f"{caminho_pdf.name}: seção {secao!r} não encontrada ou vazia"
        )
    return gabarito
