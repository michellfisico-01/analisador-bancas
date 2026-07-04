"""Extração e segmentação dos cadernos de prova do CEBRASPE.

Os cadernos têm duas colunas por página. A segmentação usa três sinais:

1. **Layout**: linhas na margem esquerda são início de item ou texto
   motivador; linhas com recuo de ~10-26 pt são continuação do item aberto;
   recuos maiores são prosa do motivador (recuo de parágrafo).
2. **Tipografia**: o número do item é impresso em fonte >= 7 pt (negrito nos
   cadernos novos). A numeração de LINHA dos textos motivadores (1, 4, 7...)
   usa fonte de 5-6 pt — é assim que as duas coisas se distinguem.
3. **Sequência**: um item só é aceito se o número for exatamente o próximo
   esperado (1, 2, 3...). Isso elimina falsos positivos restantes.

Cada bloco de itens fica vinculado ao texto motivador que o antecede
(comando "julgue os itens..." e, quando houver, o texto de apoio).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import pdfplumber

# Linhas de ruído: cabeçalhos, marcas d'água de matrícula, espaço livre.
PADROES_RUIDO = (
    re.compile(r"CEBRASPE\s*[–\-—]"),          # cabeçalho "CEBRASPE – PF ..."
    re.compile(r"^\|\|.*\|\|$"),                # marca d'água ||DPRF13_001_01N9620||
    re.compile(r"^Matriz_\S+"),                 # marca d'água Matriz_408_...N245245
    re.compile(r"^\S+_\d{3}_\d{2}N\d+"),        # variação da marca d'água
    re.compile(r"Espa[çc]o\s+livre", re.I),
    re.compile(r"^www\.cebraspe\.org\.br"),
    re.compile(r"^\(cid:\d+\)"),
)
# Bullets das páginas de instruções (o glifo varia com a fonte embutida)
PREFIXOS_INSTRUCAO = ('\u2022', '\uf0b7', '\uf02d', '\u25aa')

RE_BLOCO = re.compile(r"^BLOCO\s+([IVX]+)$")
# Fim da parte objetiva: título em CAIXA ALTA (itens podem citar a prova
# discursiva em minúsculas no meio do texto — isso não pode encerrar nada)
RE_FIM_OBJETIVA = re.compile(r"PROVA\s+DISCURSIVA")
# Capa do caderno (só existe em alguns anos): página inteira a ignorar
RE_CAPA = re.compile(r"LEIA COM ATEN[ÇC][ÃA]O AS INSTRU[ÇC][ÕO]ES", re.I)

# Limiares de recuo (pt) em relação à margem esquerda da coluna
RECUO_CONTINUACAO_MIN = 8.0
RECUO_CONTINUACAO_MAX = 26.0
TAMANHO_MINIMO_FONTE_ITEM = 7.0


@dataclass
class Linha:
    """Linha de texto com os atributos usados na classificação."""

    texto: str
    dx: float            # recuo em relação à margem esquerda da coluna
    tamanho_fonte_inicio: float  # tamanho da fonte do primeiro token
    negrito_inicio: bool


@dataclass
class Bloco:
    """Um texto motivador e os itens vinculados a ele."""

    motivador: str
    itens: list[tuple[int, str]] = field(default_factory=list)  # (numero, texto)
    rotulo_bloco: str | None = None  # "BLOCO I" etc., quando o caderno usa


@dataclass
class ResultadoExtracao:
    blocos: list[Bloco]
    avisos: list[str]

    @property
    def itens(self) -> list[tuple[int, str]]:
        return [it for b in self.blocos for it in b.itens]


def _linhas_da_coluna(coluna) -> list[Linha]:
    """Extrai as linhas de uma coluna já recortada, com recuo e fonte."""
    brutas = coluna.extract_text_lines(return_chars=True)
    if not brutas:
        return []
    # margem = menor x0 entre as linhas "normais" da coluna
    margem = min(ln["x0"] for ln in brutas)
    linhas = []
    for ln in brutas:
        texto = ln["texto"] if "texto" in ln else ln["text"]
        texto = texto.strip()
        if not texto:
            continue
        primeiro_token = texto.split()[0]
        chars_inicio = ln["chars"][: len(primeiro_token)]
        tamanho = max((c["size"] for c in chars_inicio), default=0.0)
        negrito = any("bold" in c["fontname"].lower() for c in chars_inicio)
        linhas.append(
            Linha(
                texto=texto,
                dx=ln["x0"] - margem,
                tamanho_fonte_inicio=tamanho,
                negrito_inicio=negrito,
            )
        )
    return linhas


def _eh_ruido(texto: str) -> bool:
    if any(p.search(texto) for p in PADROES_RUIDO):
        return True
    if texto.startswith(PREFIXOS_INSTRUCAO):
        return True
    # fragmentos de títulos centralizados cortados pelo recorte de coluna
    if texto in {"PROVA OBJETIVA", "-- PROVA OBJETIVA --"}:
        return True
    return False


def _inicio_item(linha: Linha, proximo: int) -> bool:
    """A linha abre o item de número `proximo`?

    Aceita também linha contendo SÓ o número: itens compostos apenas por
    figura (ex.: itens de vistas de sólidos em RLM) não têm texto na linha.
    """
    m = re.match(r"^(\d{1,3})(?:\s+\S|$)", linha.texto)
    if not m or int(m.group(1)) != proximo:
        return False
    # numeração de linha de texto motivador usa fonte pequena (5-6 pt)
    if linha.tamanho_fonte_inicio < TAMANHO_MINIMO_FONTE_ITEM:
        return False
    # itens começam na margem da coluna
    return linha.dx < RECUO_CONTINUACAO_MIN


def _limpar_linha_motivador(linha: Linha) -> str:
    """Remove a numeração de linha (fonte pequena) do início da prosa do texto."""
    m = re.match(r"^(\d{1,3})\s+(.*)$", linha.texto)
    if m and linha.tamanho_fonte_inicio < TAMANHO_MINIMO_FONTE_ITEM:
        return m.group(2)
    # linha que é SÓ o número de linha do texto (resto ficou vazio)
    if linha.texto.isdigit() and linha.tamanho_fonte_inicio < TAMANHO_MINIMO_FONTE_ITEM:
        return ""
    # fragmentos curtos em fonte pequena: sobras de subscritos de fórmulas
    if linha.tamanho_fonte_inicio < TAMANHO_MINIMO_FONTE_ITEM and len(linha.texto) <= 4:
        return ""
    return linha.texto


def segmentar_linhas(
    linhas: list[Linha], numero_inicial: int, numero_final: int
) -> ResultadoExtracao:
    """Máquina de estados que transforma linhas classificadas em blocos/itens."""
    blocos: list[Bloco] = []
    avisos: list[str] = []
    buffer_motivador: list[str] = []
    rotulo_atual: str | None = None
    item_aberto: list[str] | None = None
    numero_aberto: int | None = None
    proximo = numero_inicial

    def fechar_item() -> None:
        nonlocal item_aberto, numero_aberto
        if item_aberto is not None:
            blocos[-1].itens.append((numero_aberto, " ".join(item_aberto)))
            item_aberto, numero_aberto = None, None

    for linha in linhas:
        if proximo > numero_final:
            break
        if _eh_ruido(linha.texto):
            continue
        m_bloco = RE_BLOCO.match(linha.texto)
        if m_bloco:
            fechar_item()
            rotulo_atual = f"BLOCO {m_bloco.group(1)}"
            continue
        if RE_FIM_OBJETIVA.search(linha.texto) and proximo > numero_inicial:
            break

        if _inicio_item(linha, proximo):
            fechar_item()
            if buffer_motivador:
                blocos.append(
                    Bloco(motivador="\n".join(buffer_motivador), rotulo_bloco=rotulo_atual)
                )
                buffer_motivador = []
            if not blocos:
                blocos.append(Bloco(motivador="", rotulo_bloco=rotulo_atual))
                avisos.append(f"item {proximo}: nenhum texto motivador antes do item")
            texto_item = re.sub(r"^\d{1,3}\s*", "", linha.texto)
            if not texto_item:
                texto_item = "[item com conteúdo gráfico não extraível do PDF]"
                avisos.append(f"item {proximo}: sem texto na linha (figura?)")
            item_aberto = [texto_item]
            numero_aberto = proximo
            proximo += 1
            continue

        e_continuacao = RECUO_CONTINUACAO_MIN <= linha.dx <= RECUO_CONTINUACAO_MAX
        if item_aberto is not None and e_continuacao:
            item_aberto.append(linha.texto)
            continue

        # qualquer outra linha: prosa de motivador (fecha o item aberto)
        fechar_item()
        limpa = _limpar_linha_motivador(linha)
        if limpa:
            buffer_motivador.append(limpa)

    fechar_item()
    if proximo <= numero_final:
        avisos.append(
            f"extração parou no item {proximo - 1}; esperava chegar ao {numero_final}"
        )
    return ResultadoExtracao(blocos=blocos, avisos=avisos)


def extrair_prova(
    caminho_pdf: Path, numero_inicial: int, numero_final: int
) -> ResultadoExtracao:
    """Extrai itens e textos motivadores de um caderno de prova CEBRASPE."""
    linhas: list[Linha] = []
    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            texto_pagina = pagina.extract_text() or ""
            if RE_CAPA.search(texto_pagina):
                continue  # capa do caderno: instruções numeradas enganam o parser
            w, h = pagina.width, pagina.height
            for caixa in ((0, 0, w / 2, h), (w / 2, 0, w, h)):
                linhas.extend(_linhas_da_coluna(pagina.crop(caixa)))
    return segmentar_linhas(linhas, numero_inicial, numero_final)
