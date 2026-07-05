"""Testes da classificação (Fase 2): regras/palavras-chave e montagem do LLM.

Nenhum teste aqui chama a API — o classificador LLM é testado só na
montagem do prompt e do schema (a parte determinística).
"""
import pytest

from src.classificacao.llm import montar_schema, montar_system_prompt
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


def test_system_prompt_contem_taxonomia_e_avisos():
    prompt, disciplinas = montar_system_prompt()
    assert "Direito Constitucional" in prompt
    assert "Direito Administrativo" in prompt
    assert "Legislação Penal Especial" in prompt  # aviso de não confundir com Penal
    assert "Direito Processual Penal" in disciplinas
    assert len(disciplinas) == len(set(disciplinas))  # sem duplicatas no enum


def test_schema_estruturado_e_fechado():
    _, disciplinas = montar_system_prompt()
    schema = montar_schema(disciplinas)
    assert schema["additionalProperties"] is False
    assert set(schema["required"]) == {
        "disciplina", "topico", "subtopico", "confianca", "justificativa"
    }
    assert schema["properties"]["disciplina"]["enum"] == disciplinas
