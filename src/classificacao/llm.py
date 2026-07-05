"""Classificador de itens via API da Anthropic (JSON estruturado).

Cada item é enviado com seu texto motivador no contexto. A taxonomia
consolidada vai no system prompt (com cache: o prefixo estável é reutilizado
entre as chamadas, reduzindo muito o custo por item). A resposta é JSON
garantido por structured outputs: disciplina (enum fechado), tópico,
subtópico e confiança autodeclarada.

Controles de custo (decisão da Fase 0: o usuário controla modelo e lote):
- ``--modelo`` escolhe o modelo (padrão: claude-opus-4-8);
- ``--limite N`` classifica só N itens por execução;
- execução é retomável: itens já classificados por LLM são pulados
  (``--refazer`` força reclassificação).

A chave vem de ``ANTHROPIC_API_KEY`` no ``.env`` (nunca commitado). Sem
chave, o módulo avisa e sai sem custo algum.

Uso: ``python -m src.classificacao.llm [--limite N] [--modelo M] [--refazer]``
"""
from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

from src.classificacao.regras import CAMINHO_TAXONOMIA
from src.config import RAIZ
from src.db import conectar

MODELO_PADRAO = "claude-opus-4-8"
MAX_TOKENS_RESPOSTA = 1024


def montar_system_prompt() -> tuple[str, list[str]]:
    """Monta o system prompt com a taxonomia e devolve (prompt, disciplinas válidas)."""
    dados = json.loads(CAMINHO_TAXONOMIA.read_text(encoding="utf-8"))
    linhas = []
    disciplinas_validas: list[str] = []
    for disc in dados["disciplinas_fino"]:
        disciplinas_validas.append(disc["disciplina"])
        linhas.append(f"\n## {disc['disciplina']}")
        for topico in disc["topicos"]:
            linhas.append(f"- Tópico: {topico['topico']}")
            for sub in topico["subtopicos"]:
                linhas.append(f"  - Subtópico: {sub['nome']}")
    disciplinas_validas.extend(dados["disciplinas_grosso"])
    taxonomia_texto = "\n".join(linhas)

    prompt = f"""Você é um classificador de itens de provas de concursos públicos \
brasileiros (banca CEBRASPE, formato certo/errado, concursos PF e PRF).

Sua tarefa: dado um item (afirmação a ser julgada) e seu texto motivador, \
classificá-lo em UMA disciplina. Se a disciplina for uma das três de Direito \
detalhadas abaixo, classifique também em tópico e subtópico EXATAMENTE como \
listados na taxonomia. Para qualquer outra disciplina, tópico e subtópico \
ficam nulos.

Taxonomia das disciplinas de Direito (use os nomes literais):
{taxonomia_texto}

Demais disciplinas possíveis (sem tópico/subtópico): {", ".join(dados["disciplinas_grosso"])}.

Regras:
- O texto motivador é contexto essencial: um item curto muitas vezes só se \
entende por ele.
- "Direito Processual Penal" (inquérito, prova, prisão, ação penal) NÃO é \
"Direito Penal" (crime, pena, tipicidade). Não confunda.
- Leis penais extravagantes (drogas, armas, tortura, crimes hediondos, abuso \
de autoridade) são "Legislação Penal Especial", não "Direito Penal".
- confianca: sua confiança na classificação completa, de 0.0 a 1.0. Seja \
honesto — classificações incertas vão para revisão humana.
- justificativa: uma frase curta explicando a escolha."""
    return prompt, disciplinas_validas


def montar_schema(disciplinas_validas: list[str]) -> dict:
    """Schema JSON da resposta estruturada."""
    return {
        "type": "object",
        "properties": {
            "disciplina": {"type": "string", "enum": disciplinas_validas},
            "topico": {"type": ["string", "null"]},
            "subtopico": {"type": ["string", "null"]},
            "confianca": {"type": "number"},
            "justificativa": {"type": "string"},
        },
        "required": ["disciplina", "topico", "subtopico", "confianca", "justificativa"],
        "additionalProperties": False,
    }


def itens_pendentes(con, limite: int | None, refazer: bool) -> list[tuple]:
    """Itens a classificar (sem classificação LLM, salvo --refazer)."""
    sql = (
        "SELECT i.id, i.texto, COALESCE(m.texto, '') "
        "FROM itens i LEFT JOIN textos_motivadores m ON m.id = i.texto_motivador_id "
    )
    if not refazer:
        sql += (
            "WHERE i.id NOT IN "
            "(SELECT item_id FROM classificacoes WHERE metodo = 'llm') "
        )
    sql += "ORDER BY i.id"
    if limite:
        sql += f" LIMIT {int(limite)}"
    return con.execute(sql).fetchall()


def classificar_lote(modelo: str, limite: int | None, refazer: bool) -> int:
    """Classifica os itens pendentes via API. Devolve o total processado."""
    import anthropic  # import tardio: módulo utilizável sem SDK para testes

    load_dotenv(RAIZ / ".env")
    try:
        cliente = anthropic.Anthropic()
        # valida a credencial cedo, antes de montar o lote
        if not cliente.api_key:
            raise anthropic.AnthropicError("ANTHROPIC_API_KEY ausente")
    except Exception:
        print(
            "Chave da API não encontrada. Copie .env.example para .env e "
            "preencha ANTHROPIC_API_KEY. Nenhuma chamada foi feita (custo zero)."
        )
        return 0

    system_prompt, disciplinas_validas = montar_system_prompt()
    schema = montar_schema(disciplinas_validas)
    con = conectar()
    pendentes = itens_pendentes(con, limite, refazer)
    if not pendentes:
        print("Nenhum item pendente de classificação LLM.")
        return 0
    print(f"Classificando {len(pendentes)} itens com {modelo}...")

    processados = 0
    for item_id, texto, motivador in pendentes:
        conteudo = (
            f"TEXTO MOTIVADOR:\n{motivador or '(sem texto motivador)'}\n\n"
            f"ITEM A CLASSIFICAR:\n{texto}"
        )
        resposta = cliente.messages.create(
            model=modelo,
            max_tokens=MAX_TOKENS_RESPOSTA,
            system=[{
                "type": "text",
                "text": system_prompt,
                # prefixo estável reutilizado entre itens (reduz custo)
                "cache_control": {"type": "ephemeral"},
            }],
            output_config={"format": {"type": "json_schema", "schema": schema}},
            messages=[{"role": "user", "content": conteudo}],
        )
        if resposta.stop_reason == "refusal":
            print(f"  item {item_id}: recusado pela API, pulando")
            continue
        dados = json.loads(
            next(b.text for b in resposta.content if b.type == "text")
        )
        topico_completo = dados["disciplina"]
        if dados["topico"]:
            topico_completo += f" > {dados['topico']}"
        con.execute(
            "INSERT INTO classificacoes (item_id, metodo, topico, subtopico, confianca) "
            "VALUES (?, 'llm', ?, ?, ?) "
            "ON CONFLICT(item_id, metodo) DO UPDATE SET topico=excluded.topico, "
            "subtopico=excluded.subtopico, confianca=excluded.confianca",
            (item_id, topico_completo, dados["subtopico"], dados["confianca"]),
        )
        con.commit()  # commit por item: execução é retomável se interrompida
        processados += 1
        if processados % 25 == 0:
            print(f"  {processados}/{len(pendentes)} itens...")
    print(f"Concluído: {processados} itens classificados por LLM.")
    return processados


def main() -> int:
    parser = argparse.ArgumentParser(description="Classificador LLM (API Anthropic)")
    parser.add_argument("--modelo", default=MODELO_PADRAO)
    parser.add_argument("--limite", type=int, default=None,
                        help="classificar no máximo N itens nesta execução")
    parser.add_argument("--refazer", action="store_true",
                        help="reclassifica inclusive itens já classificados")
    args = parser.parse_args()
    classificar_lote(args.modelo, args.limite, args.refazer)
    return 0


if __name__ == "__main__":
    sys.exit(main())
