"""Download dos PDFs oficiais (provas, gabaritos definitivos e editais).

Lê o manifesto ``config/concursos.json`` e baixa cada documento para
``data/raw/{provas,gabaritos,editais}/``. Regras:

- cache local: um arquivo já baixado e válido NUNCA é baixado de novo;
- delay entre requisições reais (respeito ao servidor da banca);
- user agent identificado com contato;
- validação: resposta deve ser um PDF de verdade (magic bytes ``%PDF``).

Uso: ``python -m src.coleta.download``
"""
from __future__ import annotations

import json
import sys
import time
import unicodedata
from dataclasses import dataclass
from pathlib import Path

import requests

from src.config import (
    CAMINHO_MANIFESTO,
    DELAY_ENTRE_DOWNLOADS,
    DIR_EDITAIS,
    DIR_GABARITOS,
    DIR_PROVAS,
    USER_AGENT,
)

TAMANHO_MINIMO_PDF = 5_000  # bytes; PDFs de gabarito são pequenos, mas não tanto


@dataclass
class Documento:
    """Um documento a baixar: de onde vem, para onde vai, a que se refere."""

    url: str
    destino: Path
    concurso: str  # slug
    tipo: str  # 'prova' | 'gabarito' | 'edital'
    cargo: str | None = None


def _slug_arquivo(texto: str) -> str:
    """Normaliza um rótulo para uso em nome de arquivo (sem acentos/espaços)."""
    sem_acento = (
        unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    )
    return "".join(c if c.isalnum() else "_" for c in sem_acento).strip("_").lower()


def carregar_manifesto(caminho: Path = CAMINHO_MANIFESTO) -> dict:
    """Carrega e devolve o manifesto de coleta."""
    return json.loads(caminho.read_text(encoding="utf-8"))


def listar_documentos(manifesto: dict) -> list[Documento]:
    """Converte o manifesto na lista plana de documentos a baixar.

    O nome local é ``{slug}__{cargo}.pdf`` (prova/gabarito) ou
    ``{slug}__edital_abertura.pdf``, o que mantém rastreabilidade e evita
    colisões entre concursos.
    """
    docs: list[Documento] = []
    for conc in manifesto["concursos"]:
        slug = conc["slug"]
        for edital in conc.get("editais", []):
            docs.append(
                Documento(
                    url=edital["url"],
                    destino=DIR_EDITAIS / f"{slug}__edital_abertura.pdf",
                    concurso=slug,
                    tipo="edital",
                )
            )
        for cargo in conc.get("cargos", []):
            rotulo = _slug_arquivo(cargo["cargo"])
            docs.append(
                Documento(
                    url=cargo["prova_url"],
                    destino=DIR_PROVAS / f"{slug}__{rotulo}.pdf",
                    concurso=slug,
                    tipo="prova",
                    cargo=cargo["cargo"],
                )
            )
            docs.append(
                Documento(
                    url=cargo["gabarito_definitivo_url"],
                    destino=DIR_GABARITOS / f"{slug}__{rotulo}.pdf",
                    concurso=slug,
                    tipo="gabarito",
                    cargo=cargo["cargo"],
                )
            )
    return docs


def _pdf_valido(caminho: Path) -> bool:
    """Um arquivo em cache é válido se existe, tem tamanho razoável e é PDF."""
    if not caminho.is_file() or caminho.stat().st_size < TAMANHO_MINIMO_PDF:
        return False
    with open(caminho, "rb") as f:
        return f.read(5).startswith(b"%PDF")


def baixar(doc: Documento, sessao: requests.Session) -> str:
    """Baixa um documento (se necessário). Devolve 'cache', 'ok' ou lança exceção."""
    if _pdf_valido(doc.destino):
        return "cache"
    doc.destino.parent.mkdir(parents=True, exist_ok=True)
    resposta = sessao.get(doc.url, timeout=60)
    resposta.raise_for_status()
    conteudo = resposta.content
    if not conteudo.startswith(b"%PDF"):
        raise ValueError(
            f"resposta não é PDF (inicia com {conteudo[:8]!r}); "
            "o servidor pode ter devolvido uma página de erro"
        )
    if len(conteudo) < TAMANHO_MINIMO_PDF:
        raise ValueError(f"PDF suspeito de truncamento ({len(conteudo)} bytes)")
    # grava em arquivo temporário e renomeia: nunca deixa PDF pela metade no cache
    temporario = doc.destino.with_suffix(".baixando")
    temporario.write_bytes(conteudo)
    temporario.replace(doc.destino)
    return "ok"


def baixar_tudo(delay: float = DELAY_ENTRE_DOWNLOADS) -> dict[str, list]:
    """Baixa todos os documentos do manifesto. Devolve relatório por status."""
    docs = listar_documentos(carregar_manifesto())
    sessao = requests.Session()
    sessao.headers["User-Agent"] = USER_AGENT

    relatorio: dict[str, list] = {"ok": [], "cache": [], "erro": []}
    for doc in docs:
        try:
            status = baixar(doc, sessao)
        except Exception as erro:  # noqa: BLE001 — queremos registrar qualquer falha
            relatorio["erro"].append((doc, str(erro)))
            print(f"  ERRO   {doc.concurso:8s} {doc.tipo:8s} {doc.url}\n         -> {erro}")
            continue
        relatorio[status].append(doc)
        tamanho_kb = doc.destino.stat().st_size // 1024
        print(f"  {status.upper():6s} {doc.concurso:8s} {doc.tipo:8s} "
              f"{doc.destino.name} ({tamanho_kb} KB)")
        if status == "ok":
            time.sleep(delay)  # só espera quando de fato bateu no servidor
    return relatorio


def main() -> int:
    """Ponto de entrada da linha de comando."""
    print("Baixando documentos do manifesto config/concursos.json ...")
    relatorio = baixar_tudo()
    print(
        f"\nResumo: {len(relatorio['ok'])} baixados, "
        f"{len(relatorio['cache'])} já em cache, {len(relatorio['erro'])} erros."
    )
    return 1 if relatorio["erro"] else 0


if __name__ == "__main__":
    sys.exit(main())
