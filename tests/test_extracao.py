"""Testes das funções de extração (as mais frágeis do pipeline).

A segmentação é testada com linhas sintéticas que reproduzem os padrões
reais observados nos cadernos CEBRASPE (PF/PRF 2013-2021). Há também um
teste de integração que roda contra os PDFs baixados, quando existirem.
"""
import pytest

from src.config import DIR_GABARITOS
from src.extracao.gabarito import extrair_gabarito
from src.extracao.prova import Linha, segmentar_linhas


def linha_item(texto: str) -> Linha:
    """Linha de início de item: margem, fonte 9pt, negrito."""
    return Linha(texto=texto, dx=0.0, tamanho_fonte_inicio=9.0, negrito_inicio=True)


def linha_continuacao(texto: str) -> Linha:
    """Continuação de item: recuo de ~18pt."""
    return Linha(texto=texto, dx=17.9, tamanho_fonte_inicio=10.0, negrito_inicio=False)


def linha_motivador(texto: str, dx: float = 0.0) -> Linha:
    """Prosa de motivador na margem (ou com recuo de parágrafo)."""
    return Linha(texto=texto, dx=dx, tamanho_fonte_inicio=10.0, negrito_inicio=False)


def linha_numerada_de_texto(texto: str) -> Linha:
    """Linha de texto motivador com numeração de linha (fonte pequena)."""
    return Linha(texto=texto, dx=3.0, tamanho_fonte_inicio=5.5, negrito_inicio=False)


def test_segmentacao_basica_com_motivador():
    linhas = [
        linha_motivador("Acerca do poder de polícia, julgue os itens a seguir."),
        linha_item("1 O poder de polícia é indelegável a particulares."),
        linha_continuacao("em qualquer hipótese."),
        linha_item("2 A autoexecutoriedade dispensa ordem judicial."),
    ]
    r = segmentar_linhas(linhas, 1, 2)
    assert len(r.blocos) == 1
    assert "poder de polícia" in r.blocos[0].motivador
    assert r.itens == [
        (1, "O poder de polícia é indelegável a particulares. em qualquer hipótese."),
        (2, "A autoexecutoriedade dispensa ordem judicial."),
    ]


def test_novo_motivador_abre_novo_bloco():
    linhas = [
        linha_motivador("Julgue os itens a seguir."),
        linha_item("1 Primeiro item."),
        linha_motivador("Texto novo sobre outro assunto, julgue os próximos itens."),
        linha_item("2 Segundo item."),
    ]
    r = segmentar_linhas(linhas, 1, 2)
    assert len(r.blocos) == 2
    assert r.blocos[0].itens == [(1, "Primeiro item.")]
    assert r.blocos[1].itens == [(2, "Segundo item.")]


def test_numeracao_de_linha_de_texto_nao_vira_item():
    """Textos motivadores têm numeração de linha (1, 4, 7...) em fonte pequena."""
    linhas = [
        linha_numerada_de_texto("1 Leio que a ciência deu agora mais um passo."),
        linha_numerada_de_texto("4 mesma a cada dia... Não indaguemos para que."),
        linha_motivador("Com base no texto, julgue os itens a seguir."),
        linha_item("1 A forma verbal indica hipótese."),
    ]
    r = segmentar_linhas(linhas, 1, 1)
    assert r.itens == [(1, "A forma verbal indica hipótese.")]
    # a prosa do texto entra no motivador SEM o número de linha
    assert "Leio que a ciência" in r.blocos[0].motivador
    assert not r.blocos[0].motivador.startswith("1 ")


def test_item_somente_figura():
    """Itens compostos só por imagem têm linha contendo apenas o número."""
    linhas = [
        linha_motivador("A partir das figuras, julgue os itens a seguir."),
        linha_item("1"),
        linha_item("2"),
        linha_item("3 Item com texto normal."),
    ]
    r = segmentar_linhas(linhas, 1, 3)
    numeros = [n for n, _ in r.itens]
    assert numeros == [1, 2, 3]
    assert "gráfico" in r.itens[0][1]  # placeholder de conteúdo não extraível


def test_numero_fora_de_sequencia_nao_vira_item():
    linhas = [
        linha_motivador("Julgue os itens a seguir."),
        linha_item("1 Primeiro item."),
        linha_motivador("25, 75, 50, 150, 100, 300, 200, 600, 400, 1.200, 800, ..."),
        linha_item("2 Segundo item."),
    ]
    r = segmentar_linhas(linhas, 1, 2)
    assert [n for n, _ in r.itens] == [1, 2]
    # a sequência numérica do motivador não pode ter virado item
    assert "75" in r.blocos[1].motivador


def test_bloco_rotulado():
    linhas = [
        Linha(texto="BLOCO I", dx=100.0, tamanho_fonte_inicio=10.0, negrito_inicio=True),
        linha_motivador("Julgue os itens."),
        linha_item("1 Item do bloco um."),
    ]
    r = segmentar_linhas(linhas, 1, 1)
    assert r.blocos[0].rotulo_bloco == "BLOCO I"


GABARITO_PF21 = DIR_GABARITOS / "pf_21__agente_de_policia_federal.pdf"


@pytest.mark.skipif(not GABARITO_PF21.exists(), reason="PDF não baixado")
def test_gabarito_real_pf21_agente():
    """Integração: gabarito definitivo real do PF 2021 Agente."""
    g = extrair_gabarito(GABARITO_PF21)
    assert len(g) == 120
    assert set(g) == set(range(1, 121))
    assert g[1] == "E"
    assert g[28] == "X"  # item anulado
    assert all(r in {"C", "E", "X"} for r in g.values())
