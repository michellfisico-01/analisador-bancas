"""Padrões de "pegadinha" do CEBRASPE (Fase 3.2, parte qualitativa).

Concurseiro experiente jura que item com "somente", "sempre" ou "prescinde"
tende a estar ERRADO. Este módulo testa essa intuição nos dados: para cada
marcador linguístico clássico, mede a fração de itens ERRADOS entre os que
contêm o marcador e compara com a taxa-base da prova.

Método (mesmo padrão de honestidade do resto do projeto):
- só itens VÁLIDOS de gabarito C/E (anulados fora);
- fração de ERRADO com intervalo de credibilidade de 90% (prior de
  Jeffreys, Beta(0.5, 0.5)) — marcador raro tem intervalo largo;
- veredicto "CONFIRMADA" só quando o limite INFERIOR do IC fica acima da
  taxa-base: é evidência, não impressão;
- marcadores com menos de 10 ocorrências não recebem veredicto.

Saída: ``relatorios/pegadinhas.md`` (geral + disciplinas piloto).

Uso: ``python -m src.analise.pegadinhas``
"""
from __future__ import annotations

import re
import sys
from datetime import datetime

import pandas as pd
from scipy.stats import beta as beta_dist

from src.analise.base import DISCIPLINAS_PILOTO, carregar_itens
from src.classificacao.regras import normalizar
from src.config import DIR_RELATORIOS

N_MINIMO_VEREDICTO = 10

# Marcadores clássicos de generalização/restrição indevida em itens CEBRASPE.
# Padrões casam no texto normalizado (minúsculas, sem acento).
MARCADORES: dict[str, str] = {
    "somente / apenas / exclusivamente": r"\b(?:somente|apenas|exclusivamente)\b",
    "sempre": r"\bsempre\b",
    "nunca / jamais": r"\b(?:nunca|jamais)\b",
    "qualquer hipótese/caso": r"\bem qualquer (?:hipotese|caso|situacao)\b",
    "todos / nenhum (generalização)": r"\b(?:todos os casos|nenhuma hipotese|nenhum caso)\b",
    "independentemente": r"\bindependentemente\b",
    "obrigatoriamente / necessariamente": r"\b(?:obrigatoriamente|necessariamente)\b",
    "prescinde / dispensa / independe": r"\b(?:prescinde|prescindivel|dispensa|dispensada|dispensavel|independe)\b",
    "é vedado / não se admite": r"\b(?:e vedad[oa]|nao se admite|inadmissivel)\b",
    "privativo / exclusivo": r"\b(?:privativ[oa]|exclusiv[oa])\b",
    "desde que": r"\bdesde que\b",
    "salvo / exceto / ressalvado": r"\b(?:salvo|exceto|ressalvad[oa])\b",
}


def ic_jeffreys(erros: int, n: int, credibilidade: float = 0.90) -> tuple[float, float]:
    """IC de credibilidade para proporção com prior de Jeffreys."""
    a, b = erros + 0.5, n - erros + 0.5
    cauda = (1 - credibilidade) / 2
    return (float(beta_dist.ppf(cauda, a, b)), float(beta_dist.ppf(1 - cauda, a, b)))


def analisar_marcadores(validos: pd.DataFrame) -> pd.DataFrame:
    """Tabela: marcador, n, %ERRADO, IC90, lift sobre a taxa-base, veredicto."""
    textos = validos.texto_norm
    base_errado = (validos.gabarito == "E").mean()
    linhas = []
    for nome, padrao in MARCADORES.items():
        mask = textos.str.contains(padrao, regex=True)
        n = int(mask.sum())
        if n == 0:
            continue
        erros = int((validos[mask].gabarito == "E").sum())
        frac = erros / n
        lo, hi = ic_jeffreys(erros, n)
        if n < N_MINIMO_VEREDICTO:
            veredicto = "amostra pequena"
        elif lo > base_errado:
            veredicto = "CONFIRMADA"
        elif hi < base_errado:
            veredicto = "INVERTIDA (sinal de CERTO)"
        else:
            veredicto = "não conclusiva"
        linhas.append({
            "marcador": nome,
            "n": n,
            "pct_errado": round(frac, 3),
            "ic90": f"[{lo:.2f}, {hi:.2f}]",
            "lift": round(frac / base_errado, 2) if base_errado else None,
            "veredicto": veredicto,
        })
    return (
        pd.DataFrame(linhas)
        .sort_values(["n"], ascending=False)
        .reset_index(drop=True)
    )


def analisar_topicos(validos: pd.DataFrame) -> pd.DataFrame:
    """% ERRADO por tópico das disciplinas piloto (n >= 8)."""
    piloto = validos[validos.disciplina.isin(DISCIPLINAS_PILOTO) & validos.topico.notna()]
    linhas = []
    for (disc, topico), grupo in piloto.groupby(["disciplina", "topico"]):
        n = len(grupo)
        if n < 8:
            continue
        erros = int((grupo.gabarito == "E").sum())
        lo, hi = ic_jeffreys(erros, n)
        linhas.append({
            "disciplina": disc,
            "topico": topico,
            "n": n,
            "pct_errado": round(erros / n, 3),
            "ic90": f"[{lo:.2f}, {hi:.2f}]",
        })
    return (
        pd.DataFrame(linhas)
        .sort_values("pct_errado", ascending=False)
        .reset_index(drop=True)
    )


def main() -> int:
    itens = carregar_itens()
    validos = itens[(itens.status == "valida") & itens.gabarito.isin(["C", "E"])].copy()
    validos["texto_norm"] = validos.texto.map(normalizar)
    base_errado = (validos.gabarito == "E").mean()

    disciplinas_juridicas = list(DISCIPLINAS_PILOTO) + [
        "Direito Processual Penal", "Legislação Penal Especial",
    ]
    so_juridicos = validos[validos.disciplina.isin(disciplinas_juridicas)].copy()
    juridicos_base = (so_juridicos.gabarito == "E").mean()

    geral = analisar_marcadores(validos)
    juridicos = analisar_marcadores(so_juridicos)
    topicos = analisar_topicos(validos)

    corpo = f"""# Padrões de "pegadinha" — CEBRASPE PF/PRF

Gerado em {datetime.now():%Y-%m-%d %H:%M}. Itens válidos analisados:
{len(validos)} | taxa-base de ERRADO: **{base_errado:.1%}**.

A intuição do concurseiro diz que certos marcadores de generalização
("somente", "sempre", "prescinde"...) sinalizam item ERRADO. Aqui a
intuição vira teste estatístico: `pct_errado` entre itens com o marcador,
IC de credibilidade de 90% (prior de Jeffreys) e `lift` sobre a taxa-base.
**CONFIRMADA** = limite inferior do IC acima da taxa-base.

## Todos os itens válidos

{geral.to_markdown(index=False)}

## Só disciplinas jurídicas

Taxa-base de ERRADO nas jurídicas: {juridicos_base:.1%}.

{juridicos.to_markdown(index=False)}

## % ERRADO por tópico (disciplinas piloto, n >= 8)

Tópicos no topo são onde a banca mais "arma" o item — priorize resolver
questões (não só teoria) ao estudá-los.

{topicos.to_markdown(index=False)}
"""
    DIR_RELATORIOS.mkdir(parents=True, exist_ok=True)
    caminho = DIR_RELATORIOS / "pegadinhas.md"
    caminho.write_text(corpo, encoding="utf-8")
    print(f"Relatório: {caminho}")
    confirmadas = geral[geral.veredicto == "CONFIRMADA"]
    print(f"Intuições CONFIRMADAS no geral: {len(confirmadas)} de {len(geral)} marcadores")
    return 0


if __name__ == "__main__":
    sys.exit(main())
