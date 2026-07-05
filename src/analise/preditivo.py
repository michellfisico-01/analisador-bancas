"""Modelo preditivo de cobrança de tópicos (Fase 3.3-3.5).

Simples e interpretável, sem rede neural — cada número tem explicação:

1. **Contagem ponderada por recência**: cada item vale
   ``0.5 ** ((ano_referencia - ano_da_prova) / MEIA_VIDA)``. Com meia-vida
   de 5 anos, um item de 2021 vale ~2x um de 2016 e ~3x um de 2013.
2. **Suavização bayesiana (Dirichlet)**: sobre os tópicos do EDITAL (todos,
   inclusive os que nunca caíram), posterior Dirichlet com prior uniforme
   ``ALPHA_PRIOR`` por tópico. Tópico raro nunca tem probabilidade zero, e
   pouca evidência gera intervalo largo — a incerteza é parte da resposta.
3. **Sinal legislativo** (curadoria manual em config/eventos_legislativos.json):
   evento no tópico soma pseudo-contagens ``intensidade * decaimento`` ao
   alpha do tópico, com decaimento ``0.5 ** (anos_desde_o_evento / 2)``.
4. **Incerteza**: intervalo de credibilidade de 90% pela marginal Beta do
   Dirichlet posterior.

Saída: ``relatorios/ranking_preditivo.md`` — ranking por disciplina piloto,
geral e por órgão (PF/PRF), com probabilidade, IC90 e n efetivo.

Uso: ``python -m src.analise.preditivo``
"""
from __future__ import annotations

import json
import sys
from datetime import datetime

import pandas as pd
from scipy.stats import beta as beta_dist

from src.analise.base import DISCIPLINAS_PILOTO, carregar_itens
from src.config import DIR_CONFIG, DIR_RELATORIOS

MEIA_VIDA_ANOS = 5.0
ALPHA_PRIOR = 0.5          # prior de Jeffreys por tópico do edital
MEIA_VIDA_EVENTO = 2.0     # decaimento do efeito de mudança legislativa
CAMINHO_EVENTOS = DIR_CONFIG / "eventos_legislativos.json"
CAMINHO_TAXONOMIA = DIR_CONFIG / "taxonomias" / "consolidada.json"


def topicos_do_edital() -> dict[str, list[str]]:
    """Tópicos oficiais por disciplina piloto (universo do modelo)."""
    dados = json.loads(CAMINHO_TAXONOMIA.read_text(encoding="utf-8"))
    return {
        d["disciplina"]: [t["topico"] for t in d["topicos"]]
        for d in dados["disciplinas_fino"]
        if d["disciplina"] in DISCIPLINAS_PILOTO
    }


def pseudo_contagens_legislativas(ano_ref: int) -> dict[tuple[str, str], tuple[float, str]]:
    """(disciplina, tópico) -> (pseudo-contagem, nome do evento)."""
    if not CAMINHO_EVENTOS.exists():
        return {}
    dados = json.loads(CAMINHO_EVENTOS.read_text(encoding="utf-8"))
    extras: dict[tuple[str, str], tuple[float, str]] = {}
    for ev in dados.get("eventos", []):
        decaimento = 0.5 ** (max(0, ano_ref - ev["ano"]) / MEIA_VIDA_EVENTO)
        peso = ev.get("intensidade", 1.0) * decaimento
        marca = "" if ev.get("revisado") else " (*)"
        for alvo in ev["topicos_afetados"]:
            disc, topico = alvo.split(" > ", 1)
            atual = extras.get((disc, topico), (0.0, ""))
            extras[(disc, topico)] = (
                atual[0] + peso,
                (atual[1] + "; " if atual[1] else "") + ev["nome"] + marca,
            )
    return extras


def ranking_disciplina(
    itens: pd.DataFrame, disciplina: str, topicos: list[str],
    ano_ref: int, extras: dict,
) -> pd.DataFrame:
    """Posterior Dirichlet sobre os tópicos de uma disciplina."""
    grupo = itens[(itens.disciplina == disciplina) & itens.topico.notna()].copy()
    grupo = grupo[grupo.topico.isin(topicos)]  # descarta rótulos fora do edital
    grupo["peso"] = 0.5 ** ((ano_ref - grupo.ano) / MEIA_VIDA_ANOS)

    linhas = []
    contagens = grupo.groupby("topico").peso.sum()
    alphas = {}
    for topico in topicos:
        extra, evento = extras.get((disciplina, topico), (0.0, ""))
        alphas[topico] = ALPHA_PRIOR + contagens.get(topico, 0.0) + extra
    soma = sum(alphas.values())
    for topico in topicos:
        a = alphas[topico]
        media_posterior = a / soma
        ic = beta_dist.ppf([0.05, 0.95], a, soma - a)
        extra, evento = extras.get((disciplina, topico), (0.0, ""))
        linhas.append({
            "topico": topico,
            "prob": round(media_posterior, 3),
            "ic90": f"[{ic[0]:.3f}, {ic[1]:.3f}]",
            "n_efetivo": round(contagens.get(topico, 0.0), 1),
            "n_bruto": int((grupo.topico == topico).sum()),
            "sinal_legislativo": evento or "—",
        })
    return (
        pd.DataFrame(linhas)
        .sort_values("prob", ascending=False)
        .reset_index(drop=True)
    )


def main() -> int:
    itens = carregar_itens()
    ano_ref = int(itens.ano.max())
    universo = topicos_do_edital()
    extras = pseudo_contagens_legislativas(ano_ref)

    partes = [
        "# Ranking preditivo de tópicos — CEBRASPE PF/PRF",
        f"""Gerado em {datetime.now():%Y-%m-%d %H:%M}. Ano de referência: {ano_ref}.

**Como ler**: `prob` é a probabilidade estimada de um item da disciplina cair
naquele tópico no próximo concurso (posterior Dirichlet; contagens ponderadas
por recência com meia-vida de {MEIA_VIDA_ANOS:.0f} anos; prior {ALPHA_PRIOR} por
tópico do edital). `ic90` é o intervalo de credibilidade de 90%: intervalo
largo = pouca evidência. `sinal_legislativo` marca tópicos com mudança legal
recente (curadoria em `config/eventos_legislativos.json`; `(*)` = entrada
ainda não revisada pelo usuário).

**Cobertura**: o ranking usa só itens com rótulo fino de tópico — a cobertura
por disciplina está em `analise_descritiva.md` e melhora a cada rodada de
revisão manual (`python -m src.classificacao.revisao`).""",
    ]

    for escopo, filtro in [("Geral (PF + PRF)", None), ("PF", "PF"), ("PRF", "PRF")]:
        base = itens if filtro is None else itens[itens.orgao == filtro]
        partes.append(f"\n## {escopo}")
        for disc in DISCIPLINAS_PILOTO:
            tab = ranking_disciplina(base, disc, universo[disc], ano_ref, extras)
            n_rotulados = int(tab.n_bruto.sum())
            partes.append(f"\n### {disc} ({escopo.split(' ')[0]}) — {n_rotulados} itens rotulados\n")
            partes.append(tab.to_markdown(index=False))

    DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho = DIR_RELATORIOS / "ranking_preditivo.md"
    caminho.write_text("\n".join(partes) + "\n", encoding="utf-8")
    print(f"Ranking: {caminho}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
