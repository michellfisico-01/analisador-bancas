"""Mapeamento item -> disciplina (nível grosso, todas as disciplinas da prova).

Preenche a coluna ``itens.disciplina`` que a Fase 1 deixou NULL. Duas etapas:

1. **Item a item**: âncoras de vocabulário por disciplina (as três de Direito
   reusam as âncoras finas da taxonomia consolidada, agregadas por disciplina).
2. **Voto por bloco**: itens vinculados ao mesmo texto motivador pertencem à
   mesma disciplina no formato CEBRASPE. O voto majoritário dos itens
   classificados do bloco preenche os não classificados — e sinaliza
   discordância interna (indício de erro) no relatório.

Itens que sobrarem sem disciplina ficam NULL e vão para o modelo local
(Camada 2) e(ou) revisão manual.

Uso: ``python -m src.classificacao.disciplinas``
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict

from src.classificacao.regras import Ancora, _compilar, carregar_alvos, normalizar
from src.db import conectar

# Âncoras das disciplinas fora do núcleo de Direito (nível grosso).
# Frases valem 2.0, palavras isoladas 1.0 — mesma lógica do baseline.
ANCORAS_GROSSO: dict[str, list[str]] = {
    "Língua Portuguesa": [
        "aspectos linguísticos", "correção gramatical", "sentidos do texto",
        "sentido original do texto", "vocábulo", "concordância", "regência",
        "período do texto", "parágrafo do texto", "coesão", "pontuação",
        "manual de redação", "redação oficial", "gêneros textuais",
        "função sintática", "forma verbal", "acentuação", "crase",
        "ideias do texto", "compreensão do texto",
    ],
    "Raciocínio Lógico-Matemático": [
        "proposição", "tabela-verdade", "argumento válido", "sequência numérica",
        "progressão aritmética", "progressão geométrica", "equação", "função afim",
        "função quadrática", "porcentagem", "probabilidade", "análise combinatória",
        "regra de três", "conjuntos", "n-ésimo termo", "razão e proporção",
    ],
    "Estatística": [
        "desvio padrão", "média aritmética", "mediana", "distribuição de frequência",
        "variância", "amostra aleatória", "coeficiente de variação", "histograma",
        "distribuição normal", "quartil",
    ],
    "Informática": [
        "internet", "navegador", "sítio eletrônico", "correio eletrônico",
        "sistema operacional", "computação em nuvem", "rede de computadores",
        "protocolo", "malware", "vírus de computador", "antivírus", "firewall",
        "planilha", "becape", "backup", "software", "hardware", "aplicativo",
        "google chrome", "mozilla firefox", "windows", "linux",
    ],
    "Física": [
        "velocidade", "aceleração", "força de atrito", "energia cinética",
        "quantidade de movimento", "gravidade", "projétil", "movimento retilíneo",
        "campo elétrico", "circuito", "onda", "frequência", "aceleração centrípeta",
        "trabalho realizado pela força",
    ],
    "Contabilidade": [
        "balanço patrimonial", "demonstração do resultado", "patrimônio líquido",
        "lançamento contábil", "regime de competência", "ativo circulante",
        "passivo circulante", "receita financeira", "despesa administrativa",
        "escrituração", "débito e crédito", "conta contábil",
    ],
    "Ética no Serviço Público": [
        "código de ética", "conduta ética", "decoro", "moralidade no serviço público",
        "comissão de ética",
    ],
    "Geopolítica": [
        "globalização", "geopolítica", "blocos econômicos", "fronteiras do brasil",
        "território brasileiro", "ordem mundial", "integração regional",
    ],
    "Legislação de Trânsito": [
        "código de trânsito", "lei nº 9.503", "condutor", "habilitação",
        "infração de trânsito", "sinalização de trânsito", "veículo automotor",
        "placa de identificação", "rodovia", "carteira nacional de habilitação",
        "autoridade de trânsito", "reboque", "pedestre",
    ],
    "Direitos Humanos": [
        "direitos humanos", "declaração universal dos direitos humanos",
        "convenção americana", "pacto de san josé", "tratados internacionais de direitos",
        "sistema global de proteção", "dignidade da pessoa humana",
    ],
    "Legislação Penal Especial": [
        "lei nº 11.343", "tráfico de drogas", "estatuto do desarmamento",
        "lei nº 10.826", "porte de arma", "crimes hediondos", "lei nº 8.072",
        "crime de tortura", "lei nº 9.455", "abuso de autoridade", "lei nº 13.869",
        "maria da penha", "lei nº 11.340", "lavagem de dinheiro", "lei nº 9.613",
        "organização criminosa", "lei nº 12.850", "interceptação telefônica",
    ],
    "Direito Processual Penal": [
        "inquérito policial", "ação penal", "prisão em flagrante",
        "prisão preventiva", "prisão temporária", "busca e apreensão",
        "cadeia de custódia", "delegado de polícia", "autoridade policial",
        "código de processo penal", "termo circunstanciado", "audiência de custódia",
        "provas ilícitas", "indiciamento", "acareação", "polícia judiciária",
    ],
    "Execução Penal": [
        "lei de execução penal", "lei nº 7.210", "execução penal",
        "regime disciplinar diferenciado", "remição da pena", "detração",
        "progressão de regime", "regressão de regime", "livramento condicional",
        "estabelecimento penal", "penitenciária federal", "juízo da execução",
        "falta grave", "preso provisório", "trabalho do preso",
    ],
    "Legislação Institucional": [
        "lei orgânica do distrito federal", "organização básica da polícia civil",
        "regimento interno", "departamento penitenciário nacional",
        "estatuto dos policiais civis", "carreira de polícia civil",
    ],
    "Atividade de Inteligência": [
        "atividade de inteligência", "sistema brasileiro de inteligência",
        "sisbin", "lei nº 9.883", "contrainteligência", "agência brasileira de inteligência",
        "política nacional de inteligência", "salvaguarda de informações",
        "documentos sigilosos", "análise de inteligência",
    ],
    "Direito Eleitoral": [
        "código eleitoral", "lei nº 4.737", "lei nº 9.504", "lei das eleições",
        "justiça eleitoral", "alistamento eleitoral", "domicílio eleitoral",
        "propaganda eleitoral", "inelegibilidade", "lei complementar nº 64",
        "tribunal superior eleitoral", "tribunal regional eleitoral",
        "prestação de contas de campanha", "crimes eleitorais", "zona eleitoral",
        "título de eleitor", "urna eletrônica", "ficha limpa",
    ],
    "Direito Civil e Processual Civil": [
        "código civil", "lei nº 10.406", "código de processo civil",
        "lei nº 13.105", "negócio jurídico", "pessoa jurídica de direito privado",
        "prescrição e decadência", "petição inicial", "tutela provisória",
        "apelação", "agravo de instrumento", "coisa julgada", "litisconsórcio",
    ],
    "Administração": [
        "gestão de pessoas", "planejamento estratégico", "governança",
        "avaliação de desempenho", "estrutura organizacional",
        "departamentalização", "gestão por competências", "liderança",
        "administração pública gerencial", "gestão de processos",
    ],
    "Administração Financeira e Orçamentária": [
        "orçamento público", "plano plurianual", "lei orçamentária anual",
        "diretrizes orçamentárias", "créditos adicionais", "receita pública",
        "despesa pública", "empenho", "restos a pagar", "ciclo orçamentário",
    ],
}


# Nome da disciplina no edital -> rótulo canônico usado no banco.
# "NOÇÕES DE DIREITO PENAL E DE DIREITO PROCESSUAL PENAL" (PF) vira as duas
# disciplinas + Legislação Penal Especial, que o edital lista à parte.
MAPA_EDITAL_CANONICO: list[tuple[str, list[str]]] = [
    ("PORTUGUESA", ["Língua Portuguesa"]),
    ("PENAL E DE DIREITO PROCESSUAL", ["Direito Penal", "Direito Processual Penal"]),
    ("PROCESSUAL PENAL", ["Direito Processual Penal"]),
    ("DIREITO PENAL", ["Direito Penal"]),
    ("DIREITO ADMINISTRATIVO", ["Direito Administrativo"]),
    ("DIREITO CONSTITUCIONAL", ["Direito Constitucional"]),
    ("LEGISLAÇÃO ESPECIAL", ["Legislação Penal Especial"]),
    ("ESTATÍSTICA", ["Estatística"]),
    ("RACIOCÍNIO", ["Raciocínio Lógico-Matemático"]),
    ("MATEMÁTICA", ["Raciocínio Lógico-Matemático"]),
    ("INFORMÁTICA", ["Informática"]),
    ("CONTABILIDADE", ["Contabilidade"]),
    ("FÍSICA", ["Física"]),
    ("ÉTICA", ["Ética no Serviço Público"]),
    ("GEOPOLÍTICA", ["Geopolítica"]),
    ("TRÂNSITO", ["Legislação de Trânsito"]),
    ("DIREITOS HUMANOS", ["Direitos Humanos"]),
    ("ESTRANGEIRA", ["Língua Estrangeira"]),
    ("INGLESA", ["Língua Estrangeira"]),
    ("ESPANHOLA", ["Língua Estrangeira"]),
    ("DPRF", ["Outros"]),
    ("CIDADANIA", ["Direitos Humanos"]),
    # expansão Fase 6b (TSE/tribunais)
    ("DIREITO ELEITORAL", ["Direito Eleitoral"]),
    ("PROCESSUAL CIVIL", ["Direito Civil e Processual Civil"]),
    ("DIREITO CIVIL", ["Direito Civil e Processual Civil"]),
    ("LICITAÇÕES", ["Direito Administrativo"]),
    ("ORÇAMENT", ["Administração Financeira e Orçamentária"]),
    ("ADMINISTRAÇÃO FINANCEIRA", ["Administração Financeira e Orçamentária"]),
    ("ADMINISTRAÇÃO", ["Administração"]),
    ("GESTÃO", ["Administração"]),
    ("AUDITORIA", ["Outros"]),
    ("SEGURANÇA JUDICIÁRIA", ["Outros"]),
    ("PDPJ", ["Informática"]),
    # expansão Fase 6a (PCDF/DEPEN/ABIN)
    ("INTELIG", ["Atividade de Inteligência"]),
    ("EXECUÇÃO PENAL", ["Execução Penal"]),
    ("PENITENCIÁRIO NACIONAL", ["Legislação Institucional"]),
    ("DISTRITO FEDERAL", ["Realidade do DF"]),
    ("ATUALIDADES", ["Atualidades"]),
    # áreas de conhecimento fora do produto (ABIN CE etc.) -> Outros
    ("DIREITO INTERNACIONAL", ["Outros"]),
    ("HISTÓRIA", ["Outros"]),
    ("GEOGRAFIA", ["Outros"]),
    ("POLÍTICA E SEGURANÇA", ["Outros"]),
    ("CIÊNCIA POLÍTICA", ["Outros"]),
    ("CIÊNCIAS SOCIAIS", ["Outros"]),
    ("RELAÇÕES INTERNACIONAIS", ["Outros"]),
    ("REDES DE COMPUTADORES", ["Informática"]),
    # "LEGISLAÇÃO" genérica por último: só casa se nenhuma variante
    # específica (ESPECIAL, TRÂNSITO, DPRF...) tiver casado antes
    ("LEGISLAÇÃO", ["Legislação Institucional"]),
]


def disciplinas_do_edital(slug: str) -> set[str]:
    """Disciplinas canônicas presentes no edital do concurso `slug`."""
    import json

    from src.classificacao.taxonomia import DIR_TAXONOMIAS

    dados = json.loads((DIR_TAXONOMIAS / f"{slug}.json").read_text(encoding="utf-8"))
    presentes: set[str] = set()
    for nome_edital in dados["disciplinas"]:
        nome_upper = nome_edital.upper()
        for chave, canonicas in MAPA_EDITAL_CANONICO:
            if chave in nome_upper:
                presentes.update(canonicas)
                break
    return presentes


# Disciplinas cujo vocabulário aparece em narrativas-tema de outras questões
# (a "situação hipotética policial" contamina motivadores de RLM/Estatística)
DISCIPLINAS_JURIDICAS = {
    "Direito Constitucional", "Direito Administrativo", "Direito Penal",
    "Direito Processual Penal", "Legislação Penal Especial", "Direitos Humanos",
    "Execução Penal", "Direito Eleitoral", "Direito Civil e Processual Civil",
}


def montar_alvos_disciplina() -> dict[str, list[Ancora]]:
    """Âncoras por disciplina: as de nível grosso + as finas agregadas."""
    alvos: dict[str, list[Ancora]] = defaultdict(list)
    for disciplina, ancoras in ANCORAS_GROSSO.items():
        for a in ancoras:
            n = normalizar(a)
            peso = 2.0 if " " in n else 1.0
            alvos[disciplina].append(Ancora(padrao=_compilar(n), peso=peso, rotulo=n))
    # disciplinas de Direito: agrega as âncoras finas da taxonomia consolidada
    for alvo_fino in carregar_alvos():
        alvos[alvo_fino.disciplina].extend(alvo_fino.ancoras)
    return dict(alvos)


def classificar_item(texto: str, alvos: dict[str, list[Ancora]]) -> tuple[str | None, float]:
    """Melhor disciplina para um item isolado (sem motivador) e sua pontuação."""
    contexto = normalizar(texto)
    melhor, melhor_score = None, 0.0
    for disciplina, ancoras in alvos.items():
        score = sum(a.peso for a in ancoras if a.padrao.search(contexto))
        if score > melhor_score:
            melhor, melhor_score = disciplina, score
    return melhor, melhor_score


def mapear(con) -> dict[str, int]:
    """Roda o mapeamento em três etapas e grava itens.disciplina.

    1. item a item, restrito às disciplinas do edital daquele concurso;
    2. voto majoritário por bloco (mesmo texto motivador = mesma disciplina);
    3. interpolação: blocos sem sinal cercados pela MESMA disciplina dos dois
       lados herdam essa disciplina (o caderno agrupa disciplinas em faixas
       contíguas de itens).
    """
    alvos_todos = montar_alvos_disciplina()
    itens = con.execute(
        "SELECT i.id, i.prova_id, i.texto_motivador_id, i.numero, i.texto, "
        "COALESCE(m.texto,''), c.slug "
        "FROM itens i LEFT JOIN textos_motivadores m ON m.id = i.texto_motivador_id "
        "JOIN provas p ON p.id = i.prova_id JOIN concursos c ON c.id = p.concurso_id"
    ).fetchall()

    # âncoras filtradas por concurso: só disciplinas que existem naquele edital
    alvos_por_slug: dict[str, dict[str, list[Ancora]]] = {}
    for slug in {linha[6] for linha in itens}:
        permitidas = disciplinas_do_edital(slug)
        alvos_por_slug[slug] = {
            d: a for d, a in alvos_todos.items() if d in permitidas
        }

    # etapa 1: item a item (motivador entra com meio peso). Guarda também se o
    # voto veio do texto do PRÓPRIO item: motivador sozinho não pode decidir um
    # bloco (problemas de RLM com tema policial enganam âncoras jurídicas).
    voto_item: dict[int, str | None] = {}
    voto_proprio: dict[int, bool] = {}
    for item_id, _prova, _mot, _num, texto, motivador, slug in itens:
        alvos = alvos_por_slug[slug]
        disc_i, score_i = classificar_item(texto, alvos)
        disc_m, score_m = classificar_item(motivador, alvos) if motivador else (None, 0.0)
        if disc_i and disc_m == disc_i:
            voto_item[item_id] = disc_i
        elif disc_i and score_i >= score_m * 0.5:
            voto_item[item_id] = disc_i
        elif disc_m and score_m * 0.5 > score_i:
            voto_item[item_id] = disc_m
        else:
            voto_item[item_id] = disc_i  # pode ser None
        voto_proprio[item_id] = disc_i is not None and voto_item[item_id] == disc_i

    # etapa 2: voto majoritário por bloco — contam só votos com sinal no
    # próprio item; bloco sem nenhum voto próprio fica sem disciplina
    blocos: dict[tuple, list[int]] = defaultdict(list)
    for item_id, prova_id, motivador_id, _num, _t, _m, _s in itens:
        if motivador_id is not None:
            blocos[(prova_id, motivador_id)].append(item_id)

    discordantes = 0
    for _chave, ids in blocos.items():
        tem_voto_proprio = any(voto_item[i] and voto_proprio[i] for i in ids)
        if tem_voto_proprio:
            # com sinal em texto próprio no bloco, TODOS os votos contam —
            # os votos via motivador diluem falsos positivos isolados
            votos = Counter(voto_item[i] for i in ids if voto_item[i])
        else:
            votos = Counter()
        if not votos:
            # Nenhum item do bloco tem sinal no próprio texto. O motivador só
            # pode decidir sozinho para disciplinas NÃO jurídicas: as provas
            # ambientam RLM/Estatística/Informática em narrativas policiais,
            # então vocabulário jurídico no motivador é evidência fraca —
            # mas um motivador de Estatística descrevendo o conjunto de dados
            # é evidência legítima.
            votos_motivador = Counter(
                voto_item[i] for i in ids
                if voto_item[i] and voto_item[i] not in DISCIPLINAS_JURIDICAS
            )
            if votos_motivador:
                votos = votos_motivador
            else:
                for i in ids:
                    if not voto_proprio[i]:
                        voto_item[i] = None
                continue
        vencedor, n_vencedor = votos.most_common(1)[0]
        if n_vencedor * 2 >= sum(votos.values()):
            for i in ids:
                if voto_item[i] != vencedor and voto_item[i] is not None:
                    discordantes += 1
                voto_item[i] = vencedor

    # etapa 3: interpolação por vizinhança dentro de cada prova
    interpolados = 0
    por_prova: dict[int, list[tuple[int, int]]] = defaultdict(list)  # prova -> [(numero, id)]
    for item_id, prova_id, _mot, numero, _t, _m, _s in itens:
        por_prova[prova_id].append((numero, item_id))
    for prova_id, pares in por_prova.items():
        pares.sort()
        ids_ordenados = [i for _, i in pares]
        seq = [voto_item[i] for i in ids_ordenados]
        n = len(seq)
        pos = 0
        while pos < n:
            if seq[pos] is None:
                fim = pos
                while fim < n and seq[fim] is None:
                    fim += 1
                antes = seq[pos - 1] if pos > 0 else None
                depois = seq[fim] if fim < n else None
                if antes is not None and antes == depois:
                    for k in range(pos, fim):
                        seq[k] = antes
                        voto_item[ids_ordenados[k]] = antes
                        interpolados += 1
                pos = fim
            else:
                pos += 1

    con.executemany(
        "UPDATE itens SET disciplina = ? WHERE id = ?",
        [(d, i) for i, d in voto_item.items()],
    )
    con.commit()

    atribuidos = sum(1 for d in voto_item.values() if d)
    return {
        "total": len(itens),
        "atribuidos": atribuidos,
        "sem_disciplina": len(itens) - atribuidos,
        "discordantes_no_bloco": discordantes,
        "interpolados": interpolados,
    }


def main() -> int:
    con = conectar()
    resumo = mapear(con)
    print(f"Itens com disciplina: {resumo['atribuidos']}/{resumo['total']} "
          f"({resumo['sem_disciplina']} sem sinal -> modelo local/revisão)")
    print(f"Votos individuais sobrescritos pelo bloco: {resumo['discordantes_no_bloco']}")
    print(f"Itens preenchidos por interpolação de vizinhança: {resumo['interpolados']}")
    print("\nDistribuição por disciplina:")
    for disc, n in con.execute(
        "SELECT COALESCE(disciplina, '(sem disciplina)'), COUNT(*) FROM itens "
        "GROUP BY disciplina ORDER BY COUNT(*) DESC"
    ).fetchall():
        print(f"  {n:5d}  {disc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
