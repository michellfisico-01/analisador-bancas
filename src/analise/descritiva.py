"""Estatística descritiva (Fase 3.1 e 3.2).

Gera ``relatorios/analise_descritiva.md`` e gráficos em
``relatorios/figuras/`` com:

- distribuição de itens por disciplina em cada concurso;
- frequência de tópicos por disciplina piloto (por órgão e por ano);
- taxa de anulação por disciplina e por tópico;
- estilo CEBRASPE: proporção de gabaritos CERTO vs ERRADO por disciplina
  e por tópico (só itens válidos — anulados ficam de fora do cálculo).

Toda tabela de nível fino declara a COBERTURA (fração de itens da
disciplina com rótulo de tópico) — dado ruim invalida análise, então a
limitação fica explícita em vez de escondida.

Uso: ``python -m src.analise.descritiva``
"""
from __future__ import annotations

import sys
from datetime import datetime

import matplotlib

matplotlib.use("Agg")  # sem janela: só gera arquivos
import matplotlib.pyplot as plt
import pandas as pd

from src.analise.base import DISCIPLINAS_PILOTO, carregar_itens
from src.config import DIR_RELATORIOS

DIR_FIGURAS = DIR_RELATORIOS / "figuras"


def tabela_md(df: pd.DataFrame) -> str:
    """DataFrame -> tabela Markdown."""
    return df.to_markdown(index=False)


def secao_distribuicao(itens: pd.DataFrame) -> str:
    tab = (
        itens.groupby(["concurso", "cargo"])
        .agg(itens=("item_id", "count"),
             anulados=("status", lambda s: int((s == "anulada").sum())),
             sem_disciplina=("disciplina", lambda s: int(s.isna().sum())))
        .reset_index()
    )
    return "## Itens por prova\n\n" + tabela_md(tab)


def secao_disciplinas(itens: pd.DataFrame) -> str:
    tab = (
        itens[itens.disciplina.notna()]
        .groupby(["orgao", "disciplina"]).size().unstack(fill_value=0).T
        .reset_index()
    )
    return "## Itens por disciplina e órgão\n\n" + tabela_md(tab)


def secao_topicos(itens: pd.DataFrame) -> tuple[str, list[str]]:
    """Frequência de tópicos nas disciplinas piloto + gráficos."""
    partes = ["## Frequência de tópicos (disciplinas piloto)"]
    figuras: list[str] = []
    for disc in DISCIPLINAS_PILOTO:
        grupo = itens[itens.disciplina == disc]
        rotulados = grupo[grupo.topico.notna()]
        if grupo.empty:
            continue
        cobertura = len(rotulados) / len(grupo)
        partes.append(
            f"\n### {disc}\n\n"
            f"Itens: {len(grupo)} | com rótulo de tópico: {len(rotulados)} "
            f"(**cobertura {cobertura:.0%}** — tópicos abaixo referem-se só aos rotulados)"
        )
        if rotulados.empty:
            continue
        freq = (
            rotulados.groupby("topico")
            .agg(itens=("item_id", "count"))
            .assign(fracao=lambda d: (d.itens / d.itens.sum()).round(3))
            .sort_values("itens", ascending=False)
            .reset_index()
        )
        partes.append("\n" + tabela_md(freq))

        # por órgão (PF x PRF), quando houver dados dos dois
        por_orgao = (
            rotulados.groupby(["topico", "orgao"]).size().unstack(fill_value=0)
        )
        if por_orgao.shape[1] > 1:
            partes.append(
                "\nPor órgão (contagens):\n\n" + tabela_md(por_orgao.reset_index())
            )

        # tendência temporal: fração do tópico dentro da disciplina por ano
        por_ano = (
            rotulados.groupby(["topico", "ano"]).size().unstack(fill_value=0)
        )
        if por_ano.shape[1] > 1:
            frac = (por_ano / por_ano.sum(axis=0)).round(2)
            frac.columns = [f"{c} (fração)" for c in frac.columns]
            partes.append(
                "\nTendência temporal (fração dos itens rotulados da disciplina "
                "no ano — ascensão/declínio a confirmar com mais dados):\n\n"
                + tabela_md(frac.reset_index())
            )

        # gráfico de barras
        DIR_FIGURAS.mkdir(parents=True, exist_ok=True)
        fig, ax = plt.subplots(figsize=(9, 0.45 * len(freq) + 1.2))
        ax.barh(freq.topico[::-1], freq.itens[::-1], color="#2c6e8f")
        ax.set_xlabel("itens")
        ax.set_title(f"{disc} — itens por tópico (cobertura {cobertura:.0%})")
        fig.tight_layout()
        nome = f"topicos_{disc.lower().replace(' ', '_')}.png"
        fig.savefig(DIR_FIGURAS / nome, dpi=130)
        plt.close(fig)
        figuras.append(nome)
    return "\n".join(partes), figuras


def secao_anulacao(itens: pd.DataFrame) -> str:
    partes = ["## Taxa de anulação"]
    tab = (
        itens[itens.disciplina.notna()]
        .groupby("disciplina")
        .agg(itens=("item_id", "count"),
             anulados=("status", lambda s: int((s == "anulada").sum())))
        .assign(taxa=lambda d: (d.anulados / d.itens).round(3))
        .sort_values("taxa", ascending=False)
        .reset_index()
    )
    partes.append("\nPor disciplina:\n\n" + tabela_md(tab))

    piloto = itens[itens.disciplina.isin(DISCIPLINAS_PILOTO) & itens.topico.notna()]
    if not piloto.empty:
        tab_t = (
            piloto.groupby(["disciplina", "topico"])
            .agg(itens=("item_id", "count"),
                 anulados=("status", lambda s: int((s == "anulada").sum())))
            .reset_index()
        )
        tab_t = tab_t[tab_t.anulados > 0].sort_values("anulados", ascending=False)
        if not tab_t.empty:
            partes.append(
                "\nTópicos com itens anulados (indício de tema onde a banca "
                "erra a mão):\n\n" + tabela_md(tab_t)
            )
    return "\n".join(partes)


def secao_estilo(itens: pd.DataFrame) -> str:
    """Proporção CERTO/ERRADO — assinatura do estilo CEBRASPE."""
    validos = itens[(itens.status == "valida") & itens.gabarito.isin(["C", "E"])]
    partes = ["## Estilo CEBRASPE: proporção de gabarito CERTO"]
    geral = (validos.gabarito == "C").mean()
    partes.append(
        f"\nGeral (todas as provas, itens válidos): **{geral:.1%} CERTO** "
        f"(n={len(validos)})"
    )
    tab = (
        validos[validos.disciplina.notna()]
        .groupby("disciplina")
        .agg(itens=("item_id", "count"),
             pct_certo=("gabarito", lambda s: round((s == "C").mean(), 3)))
        .sort_values("pct_certo", ascending=False)
        .reset_index()
    )
    partes.append("\nPor disciplina:\n\n" + tabela_md(tab))

    piloto = validos[validos.disciplina.isin(DISCIPLINAS_PILOTO) & validos.topico.notna()]
    if not piloto.empty:
        tab_t = (
            piloto.groupby(["disciplina", "topico"])
            .agg(itens=("item_id", "count"),
                 pct_certo=("gabarito", lambda s: round((s == "C").mean(), 3)))
            .reset_index()
        )
        tab_t = tab_t[tab_t.itens >= 5].sort_values("pct_certo")
        partes.append(
            "\nPor tópico (só tópicos com >= 5 itens válidos rotulados):\n\n"
            + tabela_md(tab_t)
        )
    return "\n".join(partes)


def main() -> int:
    itens = carregar_itens()
    sec_topicos, figuras = secao_topicos(itens)
    corpo = "\n\n".join([
        "# Análise descritiva — CEBRASPE PF/PRF (2013-2021)",
        f"Gerado em {datetime.now():%Y-%m-%d %H:%M}. "
        f"Total de itens: {len(itens)} em {itens.concurso.nunique()} concursos. "
        "Rótulos finos seguem a precedência manual > regras (conf. alta) > "
        "modelo > regras (conf. baixa).",
        secao_distribuicao(itens),
        secao_disciplinas(itens),
        sec_topicos,
        secao_anulacao(itens),
        secao_estilo(itens),
        "## Figuras\n\n" + "\n".join(f"- `figuras/{f}`" for f in figuras),
    ])
    DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho = DIR_RELATORIOS / "analise_descritiva.md"
    caminho.write_text(corpo + "\n", encoding="utf-8")
    print(f"Relatório: {caminho}")
    print(f"Figuras: {len(figuras)} em {DIR_FIGURAS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
