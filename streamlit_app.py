"""Dashboard do Analisador Preditivo de Bancas — interface comercial.

Jornada do usuário (concurseiro): escolher o concurso -> ver o que estudar
primeiro -> conhecer o estilo da banca -> gerar o plano de estudos. O rigor
estatístico fica acessível (expanders "para céticos"), não na cara.

Rodar: ``streamlit run streamlit_app.py``
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
from src.classificacao.regras import normalizar
from src.plano.gerador import (
    agrupar_blocos,
    cronograma_semanal,
    montar_plano,
    para_markdown,
    para_pdf,
)

COR_MARCA = "#2c6e8f"      # matiz única para magnitude (barras)
COR_INCERTEZA = "#8a949c"  # bigodes de incerteza, recessivos

CONCURSOS = {
    "Polícia Federal (PF)": "PF",
    "Polícia Rodoviária Federal (PRF)": "PRF",
    "Polícia Civil do DF (PCDF)": "PCDF",
    "Polícia Penal Federal (DEPEN)": "DEPEN",
    "ABIN — Oficial de Inteligência": "ABIN",
    "Justiça Eleitoral (TSE Unificado)": "TSE",
    "TRF da 1ª Região": "TRF1",
    "Todos os concursos": "GERAL",
}

st.set_page_config(
    page_title="Analisador Preditivo de Bancas",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(show_spinner="Carregando as provas oficiais...")
def dados() -> pd.DataFrame:
    return carregar_itens()


itens = dados()
ano_ref = int(itens.ano.max())
universo = topicos_do_edital()
extras = pseudo_contagens_legislativas(ano_ref)

# ----------------------------------------------------------------- sidebar
with st.sidebar:
    st.title("🎯 Analisador Preditivo de Bancas")
    st.caption(
        "Estude o que a banca **realmente** cobra — estatística feita sobre "
        "provas e gabaritos oficiais, não achismo."
    )
    st.divider()
    escolha = st.selectbox("**1. Qual é o seu concurso?**", list(CONCURSOS))
    orgao = CONCURSOS[escolha]
    base = itens if orgao == "GERAL" else itens[itens.orgao == orgao]

    st.markdown("**2. Seu tempo de preparação** *(para o plano)*")
    semanas = st.slider("Semanas até a prova", 4, 52, 12)
    horas = st.slider("Horas de estudo por semana", 4, 50, 15)

    st.divider()
    st.caption(
        f"Base: **{len(itens):,}".replace(",", ".")
        + f" questões oficiais** · {itens.groupby(['concurso', 'cargo']).ngroups} "
        "provas · CEBRASPE e FGV · 2013-2024"
    )

aba_estudo, aba_banca, aba_plano, aba_dados = st.tabs([
    "🎯 O que estudar primeiro",
    "🔍 Raio-X da banca",
    "📅 Meu plano de estudos",
    "📊 Os dados (para céticos)",
])

# --------------------------------------------------- aba 1: o que estudar
with aba_estudo:
    st.markdown(
        f"### Prioridades de Direito para **{escolha}**\n"
        "O tamanho de cada barra é a fração das questões da disciplina que "
        "historicamente cai em cada tópico — ajustada para valorizar provas "
        "recentes e mudanças de lei."
    )
    for disc in DISCIPLINAS_PILOTO:
        tab = ranking_disciplina(base, disc, universo[disc], ano_ref, extras)
        if tab.n_bruto.sum() == 0:
            continue
        st.divider()
        st.markdown(f"#### {disc}")

        # cards do top 3
        colunas = st.columns(3)
        for coluna, (_, linha) in zip(colunas, tab.head(3).iterrows()):
            with coluna:
                with st.container(border=True):
                    st.markdown(f"**{linha.topico}**")
                    aprox = max(1, round(linha.prob * 10))
                    st.markdown(
                        f"<span style='font-size:1.6rem;font-weight:700'>"
                        f"{linha.prob:.0%}</span> <span style='color:gray'>"
                        f"≈ {aprox} de cada 10 questões</span>",
                        unsafe_allow_html=True,
                    )
                    if linha.sinal_legislativo != "—":
                        st.markdown(
                            f"⚖️ *Lei nova no radar: {linha.sinal_legislativo}*"
                        )

        # gráfico completo: barras finas, matiz única, incerteza em cinza
        ics = tab.ic90.str.strip("[]").str.split(",", expand=True).astype(float)
        fig, ax = plt.subplots(figsize=(8.5, 0.38 * len(tab) + 0.8))
        y = range(len(tab) - 1, -1, -1)
        ax.barh(y, tab.prob, color=COR_MARCA, height=0.5)
        ax.errorbar(
            tab.prob, y,
            xerr=[(tab.prob - ics[0]).clip(lower=0), (ics[1] - tab.prob).clip(lower=0)],
            fmt="none", ecolor=COR_INCERTEZA, capsize=2.5, linewidth=1.1,
        )
        for yi, (p, _) in zip(y, tab.prob.items()):
            ax.text(float(ics[1].iloc[len(tab) - 1 - yi]) + 0.012, yi,
                    f"{tab.prob.iloc[len(tab) - 1 - yi]:.0%}",
                    va="center", fontsize=8, color="#444444")
        ax.set_yticks(list(y), tab.topico, fontsize=9)
        ax.set_xticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption(
            "O traço cinza é a margem de incerteza: quanto menor o histórico "
            "de um tópico, mais larga a faixa."
        )

    with st.expander("🔬 Como calculamos (para céticos)"):
        st.markdown(
            f"""
- Contamos as questões de cada tópico em **todas as provas oficiais** do
  recorte, dando mais peso às recentes (meia-vida de {MEIA_VIDA_ANOS:.0f}
  anos: uma prova de {ano_ref} vale o dobro de uma de {ano_ref - 5}).
- Aplicamos **suavização bayesiana** (posterior de Dirichlet com prior de
  Jeffreys): tópico que nunca caiu mantém probabilidade pequena, mas nunca
  zero — edital é promessa, não estatística.
- **Mudanças legislativas** recentes (Pacote Anticrime, Lei 14.133...) somam
  pseudo-contagens com decaimento de 2 anos de meia-vida.
- A margem exibida é o **intervalo de credibilidade de 90%**.
- Só entram rótulos de alta confiança (regras determinísticas com âncoras
  legais, modelo local validado ou revisão humana).
            """
        )

# ------------------------------------------------------- aba 2: raio-x
with aba_banca:
    st.markdown(f"### O estilo da banca em **{escolha}**")
    validos = base[(base.status == "valida") & base.gabarito.isin(["C", "E"])]

    if len(validos) >= 30:
        col1, col2, col3 = st.columns(3)
        pct_errado = (validos.gabarito == "E").mean()
        col1.metric("Itens ERRADOS (certo/errado)", f"{pct_errado:.0%}",
                    help="Fração de itens cujo gabarito definitivo é ERRADO.")
        anulados = base[base.status == "anulada"]
        col2.metric("Itens anulados", len(anulados))
        col3.metric("Questões analisadas", len(base))

        # a pegadinha confirmada
        textos = validos.texto.map(normalizar)
        marcador = textos.str.contains(r"\b(?:somente|apenas|exclusivamente)\b")
        n_marc = int(marcador.sum())
        if n_marc >= 10:
            pct_marc = (validos[marcador].gabarito == "E").mean()
            with st.container(border=True):
                st.markdown(
                    f"#### 🪤 A lenda do “somente” é verdade\n"
                    f"Nas questões com **somente / apenas / exclusivamente**, "
                    f"o gabarito é ERRADO em **{pct_marc:.0%}** dos casos "
                    f"(contra {pct_errado:.0%} na média geral). Confirmado em "
                    f"{n_marc} questões oficiais — não é mito de cursinho."
                )
        st.divider()
        st.markdown("#### Onde a banca mais marca ERRADO (por disciplina)")
        pct = (
            validos[validos.disciplina.notna()]
            .groupby("disciplina").agg(
                questoes=("item_id", "count"),
                pct_errado=("gabarito", lambda s: (s == "E").mean()),
            )
        )
        pct = pct[pct.questoes >= 15].sort_values("pct_errado")
        fig, ax = plt.subplots(figsize=(8.5, 0.38 * len(pct) + 0.8))
        ax.barh(pct.index, pct.pct_errado, color=COR_MARCA, height=0.5)
        for i, v in enumerate(pct.pct_errado):
            ax.text(v + 0.01, i, f"{v:.0%}", va="center", fontsize=8,
                    color="#444444")
        ax.set_xticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.axvline(pct_errado, color=COR_INCERTEZA, linewidth=1, linestyle="--")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption(
            f"Linha tracejada: média geral ({pct_errado:.0%}). Disciplina muito "
            "acima da média pede treino de questões, não só teoria."
        )
    else:
        st.info(
            "Este concurso usa **múltipla escolha** (A-E), então a análise "
            "certo/errado não se aplica. Veja as prioridades por tópico na "
            "primeira aba — elas valem para qualquer formato."
        )

    st.divider()
    st.markdown("#### Frequência por tópico (escolha a disciplina)")
    disc_freq = st.selectbox("Disciplina", DISCIPLINAS_PILOTO, key="freq_disc",
                             label_visibility="collapsed")
    grupo = base[base.disciplina == disc_freq]
    rotulados = grupo[grupo.topico.notna()]
    if rotulados.empty:
        st.info("Sem questões rotuladas desta disciplina neste concurso.")
    else:
        freq = rotulados.groupby("topico").size().sort_values()
        fig, ax = plt.subplots(figsize=(8.5, 0.38 * len(freq) + 0.8))
        ax.barh(freq.index, freq.values, color=COR_MARCA, height=0.5)
        for i, v in enumerate(freq.values):
            ax.text(v + 0.3, i, str(v), va="center", fontsize=8, color="#444444")
        ax.set_xticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption(
            f"{len(grupo)} questões de {disc_freq} neste recorte; "
            f"{len(rotulados)} com tópico identificado."
        )

# --------------------------------------------------------- aba 3: plano
with aba_plano:
    alvo_plano = orgao if orgao != "GERAL" else "GERAL"
    plano = montar_plano(alvo_plano, semanas, float(horas))
    semanas_cron = cronograma_semanal(plano)

    st.markdown(
        f"### Seu plano para **{escolha}**\n"
        f"**{plano.horas_totais:.0f} horas** em {semanas} semanas — "
        + " · ".join(f"{d.replace('Direito ', 'D. ')}: {h:.0f}h"
                     for d, h in plano.horas_disciplina.items())
        + f" · {plano.horas_revisao:.0f}h de revisão contínua."
    )
    st.caption(
        "Horas distribuídas na proporção do que cai: disciplina com mais "
        "questões no seu concurso ganha mais tempo; dentro dela, os tópicos "
        "mais prováveis vêm primeiro. Ciclos semanais com blocos de até 2h."
    )

    md_texto = para_markdown(plano, semanas_cron)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        caminho_pdf = Path(tmp.name)
    para_pdf(plano, semanas_cron, caminho_pdf)
    col_dl1, col_dl2 = st.columns(2)
    col_dl1.download_button(
        "⬇️ Baixar plano em PDF", caminho_pdf.read_bytes(),
        file_name=f"plano_{alvo_plano.lower()}_{semanas}sem_{horas}h.pdf",
        type="primary", width="stretch",
    )
    col_dl2.download_button(
        "⬇️ Baixar em Markdown", md_texto,
        file_name=f"plano_{alvo_plano.lower()}_{semanas}sem_{horas}h.md",
        width="stretch",
    )
    caminho_pdf.unlink(missing_ok=True)

    st.divider()
    prioridades = pd.DataFrame([
        {"Ordem": i, "Disciplina": t.disciplina, "Tópico": t.topico,
         "Fração das questões": f"{t.prob:.0%}", "Horas": t.horas,
         "⚖️ Lei nova": t.sinal_legislativo or "—"}
        for i, t in enumerate(plano.topicos, start=1)
    ])
    st.dataframe(prioridades, width="stretch", hide_index=True)

    with st.expander("📆 Ver o cronograma semana a semana"):
        for n, blocos in enumerate(semanas_cron, start=1):
            st.markdown(f"**Semana {n}**")
            for rotulo, horas_b, sessoes in agrupar_blocos(blocos):
                detalhe = f" ({sessoes} sessões)" if sessoes > 1 else ""
                st.markdown(f"- {horas_b:.2g}h{detalhe} — {rotulo}")

# --------------------------------------------------------- aba 4: dados
with aba_dados:
    st.markdown(
        "### Transparência total\n"
        "Concurseiro é um público cético — com razão. Aqui está exatamente "
        "de onde os números vêm."
    )
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Questões oficiais", len(itens))
    col2.metric("Provas", itens.groupby(["concurso", "cargo"]).ngroups)
    col3.metric("Concursos", itens.concurso.nunique())
    col4.metric("Cobertura de disciplina", f"{itens.disciplina.notna().mean():.0%}")

    st.markdown("#### Questões por concurso")
    tab_conc = (
        itens.groupby(["concurso", "ano"]).size().reset_index(name="questões")
        .sort_values("ano")
    )
    st.dataframe(tab_conc, width="stretch", hide_index=True)

    st.markdown(
        """
#### Metodologia em uma página

1. **Fonte**: exclusivamente provas, gabaritos definitivos e editais
   publicados pelas bancas (CEBRASPE e FGV) em seus sites oficiais.
2. **Extração**: cada questão é separada com validação cruzada contra o
   gabarito definitivo — hoje, 23/23 provas sem nenhuma divergência.
3. **Classificação**: camadas — regras determinísticas com âncoras legais
   ("art. 5º", "Lei 8.112"...), modelo local (TF-IDF + regressão logística,
   93% de acurácia em disciplina) e revisão humana, que sempre prevalece.
   Rótulos de baixa confiança ficam FORA das estatísticas.
4. **Predição**: frequência ponderada por recência + suavização bayesiana +
   sinal de mudanças legislativas com curadoria manual. Cada número sai com
   intervalo de credibilidade.
5. **100% local e de código aberto**: sem API paga, sem caixa-preta.
        """
    )
