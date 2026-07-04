"""Pipeline da Fase 1: PDF -> itens estruturados -> SQLite -> relatório de qualidade.

Para cada prova do manifesto:
1. extrai o gabarito definitivo (fonte da verdade para a numeração dos itens);
2. extrai e segmenta o caderno de prova;
3. cruza os dois (todo item extraído precisa existir no gabarito e vice-versa);
4. grava concurso/prova/motivadores/itens no SQLite;
5. acumula métricas para o relatório de qualidade.

Uso: ``python -m src.extracao.pipeline``
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from src.coleta.download import carregar_manifesto, listar_documentos
from src.config import DIR_RELATORIOS
from src.db import conectar
from src.extracao.gabarito import extrair_gabarito
from src.extracao.prova import extrair_prova


@dataclass
class QualidadeProva:
    """Métricas de qualidade da extração de uma prova."""

    concurso: str
    cargo: str
    itens_esperados: int
    itens_gabarito: int = 0
    itens_extraidos: int = 0
    numeros_faltantes: list[int] = field(default_factory=list)
    numeros_sobrando: list[int] = field(default_factory=list)
    anulados: int = 0
    itens_sem_motivador: int = 0
    blocos: int = 0
    avisos: list[str] = field(default_factory=list)
    erro: str | None = None

    @property
    def ok(self) -> bool:
        return (
            self.erro is None
            and self.itens_extraidos == self.itens_esperados
            and not self.numeros_faltantes
            and not self.numeros_sobrando
        )


def _mapa_arquivos() -> dict[tuple[str, str, str], Path]:
    """Indexa os destinos locais dos PDFs por (slug, tipo, cargo)."""
    docs = listar_documentos(carregar_manifesto())
    return {(d.concurso, d.tipo, d.cargo or ""): d.destino for d in docs}


def processar_prova(con, concurso: dict, cargo: dict, arquivos) -> QualidadeProva:
    """Extrai, valida e persiste uma prova. Devolve as métricas de qualidade."""
    slug, nome_cargo = concurso["slug"], cargo["cargo"]
    q = QualidadeProva(
        concurso=slug, cargo=nome_cargo, itens_esperados=cargo["itens_esperados"]
    )
    pdf_prova = arquivos[(slug, "prova", nome_cargo)]
    pdf_gab = arquivos[(slug, "gabarito", nome_cargo)]

    gabarito = extrair_gabarito(pdf_gab)
    q.itens_gabarito = len(gabarito)
    q.anulados = sum(1 for r in gabarito.values() if r == "X")

    numeros = sorted(gabarito)
    resultado = extrair_prova(pdf_prova, numeros[0], numeros[-1])
    q.avisos = resultado.avisos
    q.blocos = len(resultado.blocos)

    extraidos = {n for n, _ in resultado.itens}
    q.itens_extraidos = len(extraidos)
    q.numeros_faltantes = sorted(set(numeros) - extraidos)
    q.numeros_sobrando = sorted(extraidos - set(numeros))

    # persiste (substitui a prova se ja existir: pipeline e idempotente)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO concursos (banca, orgao, nome, ano_prova, slug) VALUES (?,?,?,?,?) "
        "ON CONFLICT(slug) DO UPDATE SET nome=excluded.nome",
        (concurso["banca"], concurso["orgao"], concurso["nome"],
         concurso["ano_prova"], slug),
    )
    concurso_id = cur.execute(
        "SELECT id FROM concursos WHERE slug=?", (slug,)
    ).fetchone()[0]

    antiga = cur.execute(
        "SELECT id FROM provas WHERE concurso_id=? AND cargo=?", (concurso_id, nome_cargo)
    ).fetchone()
    if antiga:
        cur.execute("DELETE FROM itens WHERE prova_id=?", (antiga[0],))
        cur.execute("DELETE FROM textos_motivadores WHERE prova_id=?", (antiga[0],))
        cur.execute("DELETE FROM provas WHERE id=?", (antiga[0],))

    cur.execute(
        "INSERT INTO provas (concurso_id, cargo, formato, arquivo_prova, "
        "arquivo_gabarito, itens_esperados) VALUES (?,?,?,?,?,?)",
        (concurso_id, nome_cargo, concurso["formato"],
         str(pdf_prova), str(pdf_gab), cargo["itens_esperados"]),
    )
    prova_id = cur.lastrowid

    for posicao, bloco in enumerate(resultado.blocos, start=1):
        motivador_id = None
        if bloco.motivador.strip():
            cur.execute(
                "INSERT INTO textos_motivadores (prova_id, posicao, texto) VALUES (?,?,?)",
                (prova_id, posicao, bloco.motivador),
            )
            motivador_id = cur.lastrowid
        for numero, texto in bloco.itens:
            resposta = gabarito.get(numero)
            status = "anulada" if resposta == "X" else "valida"
            cur.execute(
                "INSERT INTO itens (prova_id, numero, texto, texto_motivador_id, "
                "bloco, gabarito, status) VALUES (?,?,?,?,?,?,?)",
                (prova_id, numero, texto, motivador_id, bloco.rotulo_bloco,
                 None if resposta == "X" else resposta, status),
            )
            if motivador_id is None:
                q.itens_sem_motivador += 1
    con.commit()
    return q


def gerar_relatorio(qualidades: list[QualidadeProva]) -> str:
    """Monta o relatório de qualidade em Markdown."""
    linhas = [
        "# Relatório de qualidade da extração",
        "",
        f"Gerado em {datetime.now():%Y-%m-%d %H:%M}.",
        "",
        "| Concurso | Cargo | Esperados | Gabarito | Extraídos | Anulados | Blocos | Sem motivador | Status |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for q in qualidades:
        status = "OK" if q.ok else ("ERRO" if q.erro else "DIVERGENTE")
        linhas.append(
            f"| {q.concurso} | {q.cargo} | {q.itens_esperados} | {q.itens_gabarito} "
            f"| {q.itens_extraidos} | {q.anulados} | {q.blocos} "
            f"| {q.itens_sem_motivador} | {status} |"
        )
    problemas = [q for q in qualidades if not q.ok or q.avisos]
    if problemas:
        linhas += ["", "## Detalhes e avisos", ""]
        for q in problemas:
            linhas.append(f"### {q.concurso} / {q.cargo}")
            if q.erro:
                linhas.append(f"- ERRO: {q.erro}")
            if q.numeros_faltantes:
                linhas.append(f"- itens faltantes: {q.numeros_faltantes}")
            if q.numeros_sobrando:
                linhas.append(f"- itens fora do gabarito: {q.numeros_sobrando}")
            for aviso in q.avisos:
                linhas.append(f"- aviso: {aviso}")
            linhas.append("")
    return "\n".join(linhas) + "\n"


def main() -> int:
    manifesto = carregar_manifesto()
    arquivos = _mapa_arquivos()
    con = conectar()
    qualidades: list[QualidadeProva] = []

    for concurso in manifesto["concursos"]:
        for cargo in concurso["cargos"]:
            try:
                q = processar_prova(con, concurso, cargo, arquivos)
            except Exception as erro:  # noqa: BLE001 — relatorio precisa registrar tudo
                q = QualidadeProva(
                    concurso=concurso["slug"], cargo=cargo["cargo"],
                    itens_esperados=cargo["itens_esperados"], erro=str(erro),
                )
            qualidades.append(q)
            marca = "OK " if q.ok else "!! "
            print(f"{marca}{q.concurso:8s} {q.cargo:35s} "
                  f"extraidos={q.itens_extraidos}/{q.itens_esperados} "
                  f"anulados={q.anulados} blocos={q.blocos}")
            for aviso in q.avisos:
                print(f"    aviso: {aviso}")
            if q.erro:
                print(f"    ERRO: {q.erro}")

    DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho = DIR_RELATORIOS / "qualidade_extracao.md"
    caminho.write_text(gerar_relatorio(qualidades), encoding="utf-8")
    print(f"\nRelatório: {caminho}")
    total_ok = sum(q.ok for q in qualidades)
    print(f"{total_ok}/{len(qualidades)} provas extraídas sem divergência.")
    return 0 if total_ok == len(qualidades) else 1


if __name__ == "__main__":
    sys.exit(main())
