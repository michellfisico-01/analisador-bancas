"""Extração e segmentação dos cadernos de prova da FGV (múltipla escolha).

Estrutura observada (TRF1 2024), duas colunas por página:

- **cabeçalho de disciplina**: negrito, fonte >= 12 ("Língua Portuguesa",
  "Noções de Direito Administrativo"...) — a FGV imprime as seções no
  caderno, então a disciplina de cada questão vem de graça;
- **início de questão**: o NÚMERO sozinho na linha, em negrito, fonte ~9,
  na margem da coluna — validado pela sequência estrita (1, 2, 3...);
- **alternativas**: "(A)"..."(E)" na margem, continuações indentadas;
  entram no texto da questão (carregam sinal para a classificação);
- **texto de apoio compartilhado** (quando existe) vira texto motivador,
  como no parser CEBRASPE.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

TAMANHO_MIN_CABECALHO = 12.0
TAMANHO_MIN_NUMERO = 8.0
FONTE_MAX_RUIDO = 8.2  # cabeçalho/rodapé institucional da FGV

RE_NUMERO_SOZINHO = re.compile(r"^(\d{1,3})$")
RE_FIM = re.compile(r"PROVA DISCURSIVA|QUESTÃO DISCURSIVA", re.I)


@dataclass
class QuestaoFGV:
    numero: int
    texto: str
    disciplina_caderno: str | None  # nome da seção impressa no caderno


@dataclass
class BlocoFGV:
    motivador: str
    questoes: list[QuestaoFGV] = field(default_factory=list)


@dataclass
class ResultadoFGV:
    blocos: list[BlocoFGV]
    avisos: list[str]

    @property
    def questoes(self) -> list[QuestaoFGV]:
        return [q for b in self.blocos for q in b.questoes]


def _linhas(coluna) -> list[dict]:
    saida = []
    for ln in coluna.extract_text_lines(return_chars=True):
        texto = ln["text"].strip()
        if not texto:
            continue
        primeiro = texto.split()[0]
        chars = ln["chars"][: len(primeiro)]
        saida.append({
            "texto": texto,
            "tamanho": max((c["size"] for c in chars), default=0.0),
            "negrito": any("bold" in c["fontname"].lower() for c in chars),
        })
    return saida


def extrair_prova_fgv(
    caminho_pdf: Path, numero_inicial: int, numero_final: int
) -> ResultadoFGV:
    linhas: list[dict] = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            w, h = pagina.width, pagina.height
            for caixa in ((0, 0, w / 2, h), (w / 2, 0, w, h)):
                linhas.extend(_linhas(pagina.crop(caixa)))

    blocos: list[BlocoFGV] = []
    avisos: list[str] = []
    buffer_motivador: list[str] = []
    secao: str | None = None
    questao_aberta: list[str] | None = None
    numero_aberto: int | None = None
    proximo = numero_inicial

    def fechar_questao() -> None:
        nonlocal questao_aberta, numero_aberto
        if questao_aberta is not None:
            blocos[-1].questoes.append(QuestaoFGV(
                numero=numero_aberto,
                texto=" ".join(questao_aberta),
                disciplina_caderno=secao,
            ))
            questao_aberta, numero_aberto = None, None

    cabecalho_anterior = False
    for ln in linhas:
        if proximo > numero_final and questao_aberta is None:
            break
        texto = ln["texto"]
        # ruído institucional (cabeçalho/rodapé em fonte pequena)
        if ln["tamanho"] <= FONTE_MAX_RUIDO:
            cabecalho_anterior = False
            continue
        # cabeçalho de seção/disciplina (pode quebrar em mais de uma linha)
        if ln["negrito"] and ln["tamanho"] >= TAMANHO_MIN_CABECALHO:
            fechar_questao()
            if RE_FIM.search(texto) and proximo > numero_inicial:
                break
            nome = unicodedata.normalize("NFKC", texto)
            secao = f"{secao} {nome}" if cabecalho_anterior and secao else nome
            buffer_motivador = []
            cabecalho_anterior = True
            continue
        cabecalho_anterior = False
        # início de questão: número sozinho, negrito, na sequência
        m = RE_NUMERO_SOZINHO.match(texto)
        if (m and ln["negrito"] and ln["tamanho"] >= TAMANHO_MIN_NUMERO
                and int(m.group(1)) == proximo):
            fechar_questao()
            if buffer_motivador:
                blocos.append(BlocoFGV(motivador="\n".join(buffer_motivador)))
                buffer_motivador = []
            elif not blocos:
                blocos.append(BlocoFGV(motivador=""))
            questao_aberta = []
            numero_aberto = proximo
            proximo += 1
            continue
        if questao_aberta is not None:
            questao_aberta.append(texto)
        else:
            buffer_motivador.append(texto)

    fechar_questao()
    if proximo <= numero_final:
        avisos.append(
            f"extração parou na questão {proximo - 1}; esperava chegar a {numero_final}"
        )
    return ResultadoFGV(blocos=blocos, avisos=avisos)
