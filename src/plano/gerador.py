"""Gerador de plano de estudos priorizado (Fase 4).

Combina o ranking preditivo com o tempo do usuário e produz um plano na
lógica de CICLOS DE ESTUDO que o concurseiro já pratica: em vez de esgotar
uma disciplina antes da próxima, cada ciclo alterna blocos das três
disciplinas piloto, com horas proporcionais à importância de cada uma no
órgão alvo e, dentro da disciplina, aos tópicos mais prováveis.

Regras de alocação (todas explicáveis, como o resto do modelo):
- 80% das horas para estudo dos tópicos, 20% para revisão contínua;
- horas da disciplina ∝ participação da disciplina entre as três no órgão;
- horas do tópico ∝ probabilidade prevista no ranking (posterior Dirichlet);
- tópico com menos de 1h alocada vai para a "cauda": revisão leve agrupada,
  em vez de fingir precisão de minutos;
- blocos de estudo de até 2h (limite prático de foco por sessão).

Uso:
    python -m src.plano.gerador --orgao PF --semanas 12 --horas-semana 20
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime

from src.analise.base import DISCIPLINAS_PILOTO, carregar_itens
from src.analise.preditivo import (
    pseudo_contagens_legislativas,
    ranking_disciplina,
    topicos_do_edital,
)
from src.config import DIR_RELATORIOS

FRACAO_REVISAO = 0.20
HORAS_MINIMAS_TOPICO = 1.0
BLOCO_MAX_HORAS = 2.0


@dataclass
class TopicoPlano:
    disciplina: str
    topico: str
    prob: float
    horas: float
    sinal_legislativo: str = ""


@dataclass
class PlanoEstudos:
    orgao: str
    semanas: int
    horas_semana: float
    topicos: list[TopicoPlano] = field(default_factory=list)
    cauda: list[TopicoPlano] = field(default_factory=list)
    horas_disciplina: dict[str, float] = field(default_factory=dict)

    @property
    def horas_totais(self) -> float:
        return self.semanas * self.horas_semana

    @property
    def horas_revisao(self) -> float:
        return round(self.horas_totais * FRACAO_REVISAO, 1)


def montar_plano(orgao: str, semanas: int, horas_semana: float) -> PlanoEstudos:
    """Constrói o plano a partir do ranking preditivo."""
    itens = carregar_itens()
    base = itens if orgao == "GERAL" else itens[itens.orgao == orgao]
    ano_ref = int(itens.ano.max())
    universo = topicos_do_edital()
    extras = pseudo_contagens_legislativas(ano_ref)

    plano = PlanoEstudos(orgao=orgao, semanas=semanas, horas_semana=horas_semana)
    horas_estudo = plano.horas_totais * (1 - FRACAO_REVISAO)

    # peso de cada disciplina = participação entre as três no órgão
    contagem_disc = {
        d: int((base.disciplina == d).sum()) for d in DISCIPLINAS_PILOTO
    }
    total_disc = sum(contagem_disc.values()) or 1

    for disc in DISCIPLINAS_PILOTO:
        peso = contagem_disc[disc] / total_disc
        horas_disc = horas_estudo * peso
        plano.horas_disciplina[disc] = round(horas_disc, 1)
        tab = ranking_disciplina(base, disc, universo[disc], ano_ref, extras)
        for linha in tab.itertuples():
            t = TopicoPlano(
                disciplina=disc,
                topico=linha.topico,
                prob=linha.prob,
                horas=round(horas_disc * linha.prob, 1),
                sinal_legislativo="" if linha.sinal_legislativo == "—"
                else linha.sinal_legislativo,
            )
            (plano.topicos if t.horas >= HORAS_MINIMAS_TOPICO
             else plano.cauda).append(t)

    plano.topicos.sort(key=lambda t: t.horas, reverse=True)
    plano.cauda.sort(key=lambda t: t.horas, reverse=True)
    return plano


def cronograma_semanal(plano: PlanoEstudos) -> list[list[tuple[str, float]]]:
    """Distribui os tópicos em semanas, em ciclos que alternam disciplinas.

    Cada semana consome a fila de tópicos de cada disciplina na ordem de
    prioridade, em blocos de até BLOCO_MAX_HORAS, proporcional ao peso da
    disciplina na semana. Devolve, por semana, [(rotulo, horas), ...].
    """
    horas_semana_estudo = plano.horas_semana * (1 - FRACAO_REVISAO)
    total_estudo = sum(t.horas for t in plano.topicos) or 1.0

    filas: dict[str, list[TopicoPlano]] = {d: [] for d in plano.horas_disciplina}
    for t in plano.topicos:
        filas[t.disciplina].append(t)
    restante = {id(t): t.horas for t in plano.topicos}

    semanas: list[list[tuple[str, float]]] = []
    for _semana in range(plano.semanas):
        blocos: list[tuple[str, float]] = []
        orcamento = horas_semana_estudo
        # percorre disciplinas em rodízio até esgotar o orçamento da semana
        ativo = True
        while orcamento > 0.24 and ativo:
            ativo = False
            for disc, fila in filas.items():
                while fila and restante[id(fila[0])] <= 0:
                    fila.pop(0)
                if not fila or orcamento <= 0.24:
                    continue
                topico = fila[0]
                bloco = min(BLOCO_MAX_HORAS, restante[id(topico)], orcamento)
                bloco = round(bloco * 4) / 4  # arredonda a 15 min
                if bloco < 0.25:
                    # fragmento menor que 15 min: absorvido pela revisão do
                    # ciclo (senão travaria a fila com bloco de tamanho zero)
                    if restante[id(topico)] <= 0.25:
                        restante[id(topico)] = 0
                    continue
                blocos.append((f"{topico.disciplina} — {topico.topico}", bloco))
                restante[id(topico)] -= bloco
                orcamento -= bloco
                ativo = True
        blocos.append(("Revisão do ciclo (tópicos da semana + anteriores)",
                       round(plano.horas_semana * FRACAO_REVISAO, 2)))
        semanas.append(blocos)
        if all(v <= 0 for v in restante.values()):
            # plano coberto: semanas restantes viram revisão geral
            for k in range(_semana + 1, plano.semanas):
                semanas.append([("Revisão geral e simulados (plano coberto)",
                                 plano.horas_semana)])
            break
    return semanas


def para_markdown(plano: PlanoEstudos, semanas: list[list[tuple[str, float]]]) -> str:
    partes = [
        f"# Plano de estudos — {plano.orgao} (disciplinas jurídicas do piloto)",
        f"\nGerado em {datetime.now():%Y-%m-%d} pelo Analisador Preditivo de Bancas. "
        f"Parâmetros: **{plano.semanas} semanas**, **{plano.horas_semana:.0f}h/semana** "
        f"({plano.horas_totais:.0f}h no total; {plano.horas_revisao:.0f}h de revisão contínua).",
        "\n> Escopo: Direito Constitucional, Administrativo e Penal (piloto). "
        "As demais disciplinas do edital devem ser planejadas à parte por enquanto.",
        "\n## Alocação por disciplina\n",
        "| Disciplina | Horas |",
        "|---|---:|",
    ]
    for d, h in plano.horas_disciplina.items():
        partes.append(f"| {d} | {h:.1f} |")

    partes += [
        "\n## Prioridades (o que estudar, em ordem)\n",
        "| # | Disciplina | Tópico | Prob. de cobrança | Horas | Alerta legislativo |",
        "|--:|---|---|--:|--:|---|",
    ]
    for i, t in enumerate(plano.topicos, start=1):
        partes.append(
            f"| {i} | {t.disciplina} | {t.topico} | {t.prob:.1%} | {t.horas:.1f} "
            f"| {t.sinal_legislativo or '—'} |"
        )
    if plano.cauda:
        partes.append(
            "\n**Cauda (revisão leve, sem bloco dedicado)**: "
            + "; ".join(f"{t.disciplina} — {t.topico} ({t.prob:.1%})" for t in plano.cauda)
        )

    partes.append("\n## Cronograma em ciclos semanais\n")
    for n, blocos in enumerate(semanas, start=1):
        partes.append(f"### Semana {n}")
        for rotulo, horas, sessoes in agrupar_blocos(blocos):
            detalhe = f" ({sessoes} sessões)" if sessoes > 1 else ""
            partes.append(f"- {horas:.2g}h{detalhe} — {rotulo}")
        partes.append("")
    return "\n".join(partes) + "\n"


def agrupar_blocos(blocos: list[tuple[str, float]]) -> list[tuple[str, float, int]]:
    """Junta blocos do mesmo tópico na semana: (rótulo, horas totais, sessões)."""
    agregado: dict[str, list[float]] = {}
    ordem: list[str] = []
    for rotulo, horas in blocos:
        if rotulo not in agregado:
            agregado[rotulo] = []
            ordem.append(rotulo)
        agregado[rotulo].append(horas)
    return [(r, round(sum(agregado[r]), 2), len(agregado[r])) for r in ordem]


def para_pdf(plano: PlanoEstudos, semanas: list[list[tuple[str, float]]],
             caminho) -> None:
    """PDF com reportlab (fontes nativas: texto ajustado para latin-1)."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    def latin(texto: str) -> str:
        return texto.replace("—", "-").encode("latin-1", "replace").decode("latin-1")

    estilos = getSampleStyleSheet()
    historia = [
        Paragraph(latin(f"Plano de estudos — {plano.orgao}"), estilos["Title"]),
        Paragraph(latin(
            f"{plano.semanas} semanas x {plano.horas_semana:.0f}h/semana "
            f"({plano.horas_totais:.0f}h; {plano.horas_revisao:.0f}h de revisão). "
            "Disciplinas do piloto: Constitucional, Administrativo e Penal."
        ), estilos["Normal"]),
        Spacer(1, 0.4 * cm),
        Paragraph("Prioridades", estilos["Heading2"]),
    ]
    dados = [["#", "Disciplina", "Tópico", "Prob.", "Horas"]]
    for i, t in enumerate(plano.topicos, start=1):
        dados.append([str(i), latin(t.disciplina.replace("Direito ", "D. ")),
                      latin(t.topico), f"{t.prob:.0%}", f"{t.horas:.1f}"])
    tabela = Table(dados, colWidths=[1 * cm, 3.2 * cm, 8.6 * cm, 1.8 * cm, 1.8 * cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c6e8f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef4f7")]),
    ]))
    historia.append(tabela)
    historia.append(Spacer(1, 0.4 * cm))
    historia.append(Paragraph("Cronograma semanal", estilos["Heading2"]))
    for n, blocos in enumerate(semanas, start=1):
        historia.append(Paragraph(f"Semana {n}", estilos["Heading3"]))
        for rotulo, horas, sessoes in agrupar_blocos(blocos):
            detalhe = f" ({sessoes} sessões)" if sessoes > 1 else ""
            historia.append(Paragraph(latin(f"• {horas:.2g}h{detalhe} — {rotulo}"),
                                      estilos["Normal"]))
    SimpleDocTemplate(str(caminho), pagesize=A4).build(historia)


def main() -> int:
    parser = argparse.ArgumentParser(description="Gerador de plano de estudos")
    parser.add_argument("--orgao", choices=["PF", "PRF", "GERAL"], default="GERAL")
    parser.add_argument("--semanas", type=int, default=12)
    parser.add_argument("--horas-semana", type=float, default=15.0)
    args = parser.parse_args()

    plano = montar_plano(args.orgao, args.semanas, args.horas_semana)
    semanas = cronograma_semanal(plano)

    destino = DIR_RELATORIOS / "planos"
    destino.mkdir(parents=True, exist_ok=True)
    base = f"plano_{args.orgao.lower()}_{args.semanas}sem_{args.horas_semana:.0f}h"
    md = destino / f"{base}.md"
    pdf = destino / f"{base}.pdf"
    md.write_text(para_markdown(plano, semanas), encoding="utf-8")
    para_pdf(plano, semanas, pdf)
    print(f"Plano Markdown: {md}")
    print(f"Plano PDF:      {pdf}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
