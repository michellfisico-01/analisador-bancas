"""Extração de gabaritos oficiais definitivos do CEBRASPE.

Formato observado em todos os concursos do piloto (2013-2021): pares de
linhas ``Item <números>`` / ``Gabarito <respostas>``, em que ``X`` marca
item anulado e ``0`` é preenchimento de célula vazia da tabela.
"""
from __future__ import annotations

from pathlib import Path

import pdfplumber

# Respostas possíveis: C/E (certo/errado), A-E (múltipla escolha, Fase 6),
# X (anulado). '0' é lixo de preenchimento da tabela e é descartado.
RESPOSTAS_VALIDAS = set("CEX") | set("ABD")


def extrair_gabarito(caminho_pdf: Path) -> dict[int, str]:
    """Lê o PDF do gabarito definitivo e devolve {numero_item: resposta}.

    A resposta é 'C', 'E' (ou letra de múltipla escolha) ou 'X' para anulado.
    Lança ValueError se o PDF não contiver o padrão esperado ou se houver
    item duplicado — dado ruim deve estourar cedo, não passar adiante.
    """
    gabarito: dict[int, str] = {}
    with pdfplumber.open(caminho_pdf) as pdf:
        linhas: list[str] = []
        for pagina in pdf.pages:
            linhas.extend((pagina.extract_text() or "").splitlines())

    numeros_pendentes: list[int] | None = None
    for linha in linhas:
        tokens = linha.split()
        if not tokens:
            continue
        if tokens[0] == "Item":
            numeros_pendentes = [int(t) for t in tokens[1:] if t.isdigit()]
        elif tokens[0] == "Gabarito" and numeros_pendentes is not None:
            respostas = tokens[1:]
            # pareia por posição; células '0' (numero 0 ou resposta '0') são descarte
            for numero, resposta in zip(numeros_pendentes, respostas):
                if numero == 0 or resposta == "0":
                    continue
                if resposta not in RESPOSTAS_VALIDAS:
                    raise ValueError(
                        f"{caminho_pdf.name}: resposta inesperada {resposta!r} "
                        f"para o item {numero}"
                    )
                if numero in gabarito:
                    raise ValueError(
                        f"{caminho_pdf.name}: item {numero} duplicado no gabarito"
                    )
                gabarito[numero] = resposta
            numeros_pendentes = None

    if not gabarito:
        raise ValueError(
            f"{caminho_pdf.name}: nenhum par Item/Gabarito encontrado — "
            "o formato do PDF pode ter mudado"
        )
    return gabarito
