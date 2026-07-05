"""Testes do gerador de plano de estudos (Fase 4)."""
import pytest

from src.config import CAMINHO_BD
from src.plano.gerador import (
    FRACAO_REVISAO,
    agrupar_blocos,
    cronograma_semanal,
    montar_plano,
)

precisa_bd = pytest.mark.skipif(not CAMINHO_BD.exists(), reason="banco não gerado")


def test_agrupar_blocos_soma_e_conta_sessoes():
    blocos = [("A", 2.0), ("B", 1.0), ("A", 2.0), ("A", 1.5)]
    agrupado = agrupar_blocos(blocos)
    assert agrupado[0] == ("A", 5.5, 3)
    assert agrupado[1] == ("B", 1.0, 1)


@precisa_bd
def test_alocacao_respeita_orcamento_de_horas():
    plano = montar_plano("PF", semanas=10, horas_semana=10.0)
    horas_estudo = sum(t.horas for t in plano.topicos) + sum(t.horas for t in plano.cauda)
    # estudo = total menos a reserva de revisão (tolerância de arredondamento)
    assert horas_estudo == pytest.approx(100.0 * (1 - FRACAO_REVISAO), rel=0.05)
    assert sum(plano.horas_disciplina.values()) == pytest.approx(
        100.0 * (1 - FRACAO_REVISAO), rel=0.05
    )


@precisa_bd
def test_prioridades_ordenadas_por_horas():
    plano = montar_plano("GERAL", semanas=12, horas_semana=15.0)
    horas = [t.horas for t in plano.topicos]
    assert horas == sorted(horas, reverse=True)
    # cauda só tem tópicos abaixo do mínimo
    assert all(t.horas < 1.0 for t in plano.cauda)


@precisa_bd
def test_cronograma_cobre_todas_as_semanas():
    plano = montar_plano("PRF", semanas=8, horas_semana=12.0)
    semanas = cronograma_semanal(plano)
    assert len(semanas) == 8
    # nenhuma semana estoura o orçamento; as primeiras são cheias; depois de
    # cobrir os tópicos pode haver UMA semana parcial de transição antes das
    # semanas de revisão geral (a cauda fica fora do cronograma por design)
    totais = [sum(h for _, h in blocos) for blocos in semanas]
    assert all(t <= 12.0 + 0.5 for t in totais)
    assert totais[0] == pytest.approx(12.0, rel=0.1)
    assert totais[1] == pytest.approx(12.0, rel=0.1)
    # semanas parciais só existem na transição para a revisão geral (o
    # deadlock que este teste pegou produzia a MAIORIA das semanas capadas)
    parciais = [t for t in totais if t < 12.0 * 0.85]
    assert len(parciais) <= 2
