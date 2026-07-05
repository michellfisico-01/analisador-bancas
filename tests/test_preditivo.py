"""Testes da matemática do modelo preditivo (Fase 3)."""
import pandas as pd
import pytest

from src.analise.preditivo import (
    ALPHA_PRIOR,
    pseudo_contagens_legislativas,
    ranking_disciplina,
    topicos_do_edital,
)


def _itens_ficticios() -> pd.DataFrame:
    """Mini-dataset: 6 itens de Direito Penal em dois anos."""
    return pd.DataFrame({
        "item_id": range(6),
        "disciplina": ["Direito Penal"] * 6,
        "topico": ["Crimes contra a pessoa"] * 3
                  + ["Crimes contra o patrimônio"] * 2 + ["Ilicitude"],
        "ano": [2013, 2021, 2021, 2021, 2021, 2013],
        "orgao": ["PF"] * 6,
    })


TOPICOS = ["Crimes contra a pessoa", "Crimes contra o patrimônio",
           "Ilicitude", "Punibilidade"]


def test_probabilidades_somam_um():
    tab = ranking_disciplina(_itens_ficticios(), "Direito Penal", TOPICOS, 2021, {})
    assert tab.prob.sum() == pytest.approx(1.0, abs=0.01)


def test_topico_sem_ocorrencia_tem_probabilidade_positiva():
    """Suavização bayesiana: tópico do edital nunca tem probabilidade zero."""
    tab = ranking_disciplina(_itens_ficticios(), "Direito Penal", TOPICOS, 2021, {})
    punibilidade = tab[tab.topico == "Punibilidade"].iloc[0]
    assert punibilidade.prob > 0
    assert punibilidade.n_bruto == 0


def test_recencia_pesa_mais_que_passado():
    """3 itens (1 de 2013 + 2 de 2021) devem pesar menos que 3 de 2021... não:
    a contagem EFETIVA de 2013 vale ~0.33 (meia-vida 5 anos, 8 anos atrás)."""
    tab = ranking_disciplina(_itens_ficticios(), "Direito Penal", TOPICOS, 2021, {})
    pessoa = tab[tab.topico == "Crimes contra a pessoa"].iloc[0]
    # 2 itens de 2021 (peso 1.0) + 1 de 2013 (peso 0.5^(8/5) ~ 0.33)
    assert pessoa.n_efetivo == pytest.approx(2.33, abs=0.05)


def test_sinal_legislativo_eleva_probabilidade():
    extras = {("Direito Penal", "Punibilidade"): (1.0, "Evento teste")}
    sem = ranking_disciplina(_itens_ficticios(), "Direito Penal", TOPICOS, 2021, {})
    com = ranking_disciplina(_itens_ficticios(), "Direito Penal", TOPICOS, 2021, extras)
    p_sem = sem[sem.topico == "Punibilidade"].iloc[0].prob
    p_com = com[com.topico == "Punibilidade"].iloc[0].prob
    assert p_com > p_sem
    assert com[com.topico == "Punibilidade"].iloc[0].sinal_legislativo == "Evento teste"


def test_rotulo_fora_do_edital_e_descartado():
    itens = _itens_ficticios()
    itens.loc[0, "topico"] = "Tópico inventado"
    tab = ranking_disciplina(itens, "Direito Penal", TOPICOS, 2021, {})
    assert "Tópico inventado" not in set(tab.topico)


def test_universo_de_topicos_vem_da_taxonomia_aprovada():
    universo = topicos_do_edital()
    assert set(universo) == {
        "Direito Constitucional", "Direito Administrativo", "Direito Penal"
    }
    assert "Controle de constitucionalidade" in universo["Direito Constitucional"]


def test_eventos_legislativos_carregam_e_decaem():
    extras = pseudo_contagens_legislativas(2021)
    assert extras  # arquivo de curadoria existe e tem eventos
    chave_2021 = ("Direito Administrativo", "Licitações e contratos")
    chave_2019 = ("Direito Penal", "Punibilidade")
    assert extras[chave_2021][0] > extras[chave_2019][0]  # evento mais recente pesa mais
