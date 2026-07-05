"""Testes da classificação (Fase 2): Camada 1 (regras) e Camada 2 (modelo).

Tudo local, sem serviço externo — restrição de custo zero do projeto.
"""
import pytest

from src.classificacao.disciplinas import disciplinas_do_edital
from src.classificacao.modelo import _filtrar_classes_raras, montar_corpus
from src.classificacao.regras import carregar_alvos, classificar, normalizar


@pytest.fixture(scope="module")
def alvos():
    return carregar_alvos()


def test_normalizar_remove_acentos_e_caixa():
    assert normalizar("Constituição FEDERAL  de\n1988") == "constituicao federal de 1988"


def test_item_de_poder_de_policia(alvos):
    r = classificar(
        "O processo aberto contra o servidor caracteriza poder de polícia administrativo.",
        "Determinado agente da Polícia Federal revelou um segredo sobre uma operação.",
        alvos,
    )
    assert r is not None
    assert r.disciplina == "Direito Administrativo"
    assert r.topico == "Poderes administrativos"


def test_item_de_remedios_constitucionais(alvos):
    r = classificar(
        "O habeas corpus é o remédio constitucional cabível para proteger a liberdade "
        "de locomoção ameaçada por ilegalidade.",
        "",
        alvos,
    )
    assert r.disciplina == "Direito Constitucional"
    assert r.subtopico == "Remédios constitucionais"
    assert r.confianca >= 0.75  # duas âncoras fortes casam


def test_ancora_curta_nao_vaza_para_palavra_maior(alvos):
    """'PAD' não pode casar dentro de 'padrão'; 'ADI' não casa em 'tradição'."""
    r = classificar(
        "O padrão apresentado pela sequência indica tradição matemática.",
        "",
        alvos,
    )
    assert r is None or r.confianca < 0.75


def test_item_sem_ancora_devolve_none(alvos):
    r = classificar(
        "A concordância verbal do período está correta.",
        "Julgue o item quanto aos aspectos linguísticos do texto.",
        alvos,
    )
    assert r is None


def test_referencia_legal_pesa_mais_que_palavra_solta(alvos):
    """'Lei 8.112' deve levar o item para Agentes públicos com confiança alta."""
    r = classificar(
        "Nos termos da Lei nº 8.112/1990, o servidor em estágio probatório "
        "pode ser exonerado.",
        "",
        alvos,
    )
    assert r.disciplina == "Direito Administrativo"
    assert r.topico == "Agentes públicos"
    assert r.confianca >= 0.75


def test_montar_corpus_pondera_item_sobre_motivador():
    """O texto do item entra duas vezes; o motivador, uma (é só contexto)."""
    ids, docs = montar_corpus([(7, "Peculato é crime.", "Texto sobre servidor.")])
    assert ids == [7]
    assert docs[0].count("peculato") == 2
    assert docs[0].count("servidor") == 1


def test_disciplinas_do_edital_respeitam_o_programa():
    """PF não tem Geopolítica/Física/Trânsito; PRF não tem Contabilidade."""
    pf = disciplinas_do_edital("pf_21")
    assert "Contabilidade" in pf
    assert "Direito Penal" in pf  # via disciplina fundida do edital PF
    assert "Direito Processual Penal" in pf
    assert "Geopolítica" not in pf
    assert "Física" not in pf
    assert "Legislação de Trânsito" not in pf

    prf = disciplinas_do_edital("prf_21")
    assert "Legislação de Trânsito" in prf
    assert "Física" in prf
    assert "Contabilidade" not in prf


def test_filtrar_classes_raras_remove_e_reporta():
    ids = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    docs = [f"doc {i}" for i in ids]
    rotulos = ["A"] * 5 + ["B"] * 3 + ["C"]  # B tem 3 exemplos (< 4), C tem 1
    ids_f, docs_f, rotulos_f, excluidas = _filtrar_classes_raras(ids, docs, rotulos)
    assert set(rotulos_f) == {"A"}
    assert len(ids_f) == len(docs_f) == len(rotulos_f) == 5
    assert excluidas == ["B", "C"]
