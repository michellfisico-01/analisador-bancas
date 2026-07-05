"""Dashboard do Analisador Preditivo de Bancas (Fase 5).

Interface local em Streamlit sobre os módulos já testados de análise e
plano — este arquivo é só a camada de apresentação. Rodar:

    streamlit run streamlit_app.py

O nome do arquivo na raiz segue a convenção do Streamlit Community Cloud,
para publicação gratuita futura sem mudança de estrutura.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.analise.base import DISCIPLINAS_PILOTO, carregar_itens
from src.analise.preditivo import (
    MEIA_VIDA_ANOS,
    pseudo_contagens_legislativas,
    ranking_disciplina,
    topicos_do_edital,
)
from src.plano.gerador import (
    agrupar_blocos,
    cronograma_semanal,
    montar_plano,
    para_markdown,
    para_pdf,
)

st.set_page_config(
    page_title="Analisador Preditivo de Bancas",
    page_icon="📊",
    layout="wide",
)


@st.cache_data(show_spinner="Carregando itens do banco...")
def dados() -> pd.DataFrame:
    return carregar_itens()


itens = dados()
ano_ref = int(itens.ano.max())
universo = topicos_do_edital()
extras = pseudo_contagens_legislativas(ano_ref)

st.title("Analisador Preditivo de Bancas")
st.caption(
    "CEBRASPE · PF e PRF · 2013-2021 · 100% local e de custo zero. "
    "Probabilidades são posteriores bayesianos sobre provas oficiais — "
    "cada número é explicável."
)

aba_visao, aba_freq, aba_ranking, aba_plano = st.tabs(
    ["Visão geral", "Frequência de tópicos", "Ranking preditivo", "Plano de estudos"]
)

# ---------------------------------------------------------------- visão geral
with aba_visao:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Itens extraídos", len(itens))
    col2.metric("Provas", itens.groupby(["concurso", "cargo"]).ngroups)
    col3.metric("Itens anulados", int((itens.status == "anulada").sum()))
    cobertura = itens.disciplina.notna().mean()
    col4.metric("Cobertura de disciplina", f"{cobertura:.0%}")

    st.subheader("Itens por disciplina e órgão")
    tab = (
        itens[itens.disciplina.notna()]
        .groupby(["disciplina", "orgao"]).size().unstack(fill_value=0)
        .sort_values(by=list(itens.orgao.unique())[:1] or "PF", ascending=False)
    )
    st.bar_chart(tab)

    st.subheader("Estilo CEBRASPE: proporção de gabarito CERTO por disciplina")
    validos = itens[(itens.status == "valida") & itens.gabarito.isin(["C", "E"])]
    pct = (
        validos[validos.disciplina.notna()]
        .groupby("disciplina").gabarito
        .apply(lambda s: (s == "C").mean())
        .sort_values()
    )
    st.bar_chart(pct)
    st.caption(
        f"Geral: {(validos.gabarito == 'C').mean():.1%} CERTO em {len(validos)} "
        "itens válidos. Desvios fortes por disciplina são assinatura da banca."
    )

# ---------------------------------------------------------- frequência de tópicos
with aba_freq:
    col_a, col_b = st.columns(2)
    disc_sel = col_a.selectbox("Disciplina", DISCIPLINAS_PILOTO, key="freq_disc")
    orgao_sel = col_b.selectbox("Órgão", ["PF + PRF", "PF", "PRF"], key="freq_orgao")
    base = itens if orgao_sel == "PF + PRF" else itens[itens.orgao == orgao_sel]

    grupo = base[base.disciplina == disc_sel]
    rotulados = grupo[grupo.topico.notna()]
    st.caption(
        f"{len(grupo)} itens na disciplina; {len(rotulados)} com rótulo de tópico "
        f"(cobertura {len(rotulados) / max(len(grupo), 1):.0%}). A cobertura sobe "
        "a cada rodada de revisão manual."
    )
    if rotulados.empty:
        st.info("Sem itens rotulados neste recorte.")
    else:
        freq = rotulados.groupby("topico").size().sort_values()
        st.bar_chart(freq)
        detalhe = (
            rotulados.groupby("topico")
            .agg(
                itens=("item_id", "count"),
                pct_certo=("gabarito", lambda s: (s == "C").mean()),
                anulados=("status", lambda s: int((s == "anulada").sum())),
            )
            .sort_values("itens", ascending=False)
            .reset_index()
        )
        detalhe["pct_certo"] = detalhe.pct_certo.map(lambda v: f"{v:.0%}")
        st.dataframe(detalhe, width="stretch", hide_index=True)

# ------------------------------------------------------------------- ranking
with aba_ranking:
    col_a, col_b = st.columns(2)
    disc_r = col_a.selectbox("Disciplina", DISCIPLINAS_PILOTO, key="rank_disc")
    orgao_r = col_b.selectbox("Órgão", ["PF + PRF", "PF", "PRF"], key="rank_orgao")
    base_r = itens if orgao_r == "PF + PRF" else itens[itens.orgao == orgao_r]

    tab_r = ranking_disciplina(base_r, disc_r, universo[disc_r], ano_ref, extras)
    st.caption(
        f"Probabilidade de um item de {disc_r} cair em cada tópico no próximo "
        f"concurso. Contagens ponderadas por recência (meia-vida "
        f"{MEIA_VIDA_ANOS:.0f} anos), suavização de Dirichlet e IC de "
        "credibilidade de 90%. `(*)` = evento legislativo ainda não revisado."
    )

    ics = tab_r.ic90.str.strip("[]").str.split(",", expand=True).astype(float)
    fig, ax = plt.subplots(figsize=(8, 0.42 * len(tab_r) + 1))
    y = range(len(tab_r) - 1, -1, -1)
    ax.barh(y, tab_r.prob, color="#2c6e8f", height=0.55)
    ax.errorbar(
        tab_r.prob, y,
        xerr=[tab_r.prob - ics[0], ics[1] - tab_r.prob],
        fmt="none", ecolor="#e07b39", capsize=3, linewidth=1.4,
    )
    ax.set_yticks(list(y), tab_r.topico)
    ax.set_xlabel("probabilidade (barra) e IC 90% (traço)")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    st.dataframe(tab_r, width="stretch", hide_index=True)

# -------------------------------------------------------------------- plano
with aba_plano:
    st.subheader("Gerar plano de estudos personalizado")
    col_a, col_b, col_c = st.columns(3)
    orgao_p = col_a.selectbox("Concurso alvo", ["PF", "PRF", "GERAL"], key="plano_orgao")
    semanas_p = col_b.slider("Semanas até a prova", 4, 52, 12)
    horas_p = col_c.slider("Horas de estudo por semana", 4, 50, 15)

    plano = montar_plano(orgao_p, semanas_p, float(horas_p))
    semanas_cron = cronograma_semanal(plano)

    st.caption(
        f"{plano.horas_totais:.0f}h no total — "
        + " · ".join(f"{d.replace('Direito ', 'D. ')}: {h:.0f}h"
                     for d, h in plano.horas_disciplina.items())
        + f" · revisão contínua: {plano.horas_revisao:.0f}h. "
        "Escopo: disciplinas jurídicas do piloto."
    )

    prioridades = pd.DataFrame([
        {"#": i, "Disciplina": t.disciplina, "Tópico": t.topico,
         "Prob.": f"{t.prob:.1%}", "Horas": t.horas,
         "Alerta legislativo": t.sinal_legislativo or "—"}
        for i, t in enumerate(plano.topicos, start=1)
    ])
    st.dataframe(prioridades, width="stretch", hide_index=True)

    with st.expander("Cronograma semana a semana"):
        for n, blocos in enumerate(semanas_cron, start=1):
            st.markdown(f"**Semana {n}**")
            for rotulo, horas, sessoes in agrupar_blocos(blocos):
                detalhe = f" ({sessoes} sessões)" if sessoes > 1 else ""
                st.markdown(f"- {horas:.2g}h{detalhe} — {rotulo}")

    md_texto = para_markdown(plano, semanas_cron)
    col_dl1, col_dl2 = st.columns(2)
    col_dl1.download_button(
        "Baixar plano (Markdown)", md_texto,
        file_name=f"plano_{orgao_p.lower()}_{semanas_p}sem_{horas_p}h.md",
    )
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        caminho_pdf = Path(tmp.name)
    para_pdf(plano, semanas_cron, caminho_pdf)
    col_dl2.download_button(
        "Baixar plano (PDF)", caminho_pdf.read_bytes(),
        file_name=f"plano_{orgao_p.lower()}_{semanas_p}sem_{horas_p}h.pdf",
    )
    caminho_pdf.unlink(missing_ok=True)
