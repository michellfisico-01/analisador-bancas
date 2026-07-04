"""Testes de integridade do manifesto de coleta (config/concursos.json)."""
import re

import pytest

from src.coleta.download import carregar_manifesto, listar_documentos

HOSTS_PERMITIDOS = ("cdn.cebraspe.org.br", "www.cespe.unb.br")


@pytest.fixture(scope="module")
def manifesto():
    return carregar_manifesto()


def test_todo_concurso_tem_campos_obrigatorios(manifesto):
    for conc in manifesto["concursos"]:
        for campo in ("slug", "banca", "orgao", "nome", "ano_prova", "formato", "cargos"):
            assert campo in conc, f"{conc.get('slug', '?')}: falta campo '{campo}'"
        assert conc["formato"] in ("certo_errado", "multipla_escolha")


def test_urls_apontam_para_fontes_oficiais(manifesto):
    """Garante que só coletamos de fontes oficiais da banca (regra do projeto)."""
    for doc in listar_documentos(manifesto):
        host = re.match(r"https?://([^/]+)/", doc.url).group(1)
        assert host in HOSTS_PERMITIDOS, f"host não oficial: {host} em {doc.url}"


def test_destinos_locais_sao_unicos(manifesto):
    """Dois documentos nunca podem sobrescrever o mesmo arquivo local."""
    destinos = [doc.destino for doc in listar_documentos(manifesto)]
    assert len(destinos) == len(set(destinos))


def test_cada_cargo_tem_prova_e_gabarito(manifesto):
    for conc in manifesto["concursos"]:
        for cargo in conc["cargos"]:
            assert cargo["prova_url"].lower().endswith(".pdf")
            assert cargo["gabarito_definitivo_url"].lower().endswith(".pdf")
            assert "DEFINITIVO" in cargo["gabarito_definitivo_url"].upper() or (
                "Gab_Definitivo" in cargo["gabarito_definitivo_url"]
            ), (
                f"{conc['slug']}/{cargo['cargo']}: gabarito não parece ser o DEFINITIVO "
                "(regra do projeto: nunca usar o preliminar)"
            )
            assert cargo["itens_esperados"] > 0


def test_piloto_cobre_os_cinco_concursos(manifesto):
    slugs = {c["slug"] for c in manifesto["concursos"]}
    assert slugs == {"dprf_13", "pf_18", "prf_18", "pf_21", "prf_21"}
