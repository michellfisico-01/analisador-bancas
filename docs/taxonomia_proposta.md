# Taxonomia proposta — disciplinas de Direito (Fase 2)

> **Status: RASCUNHO PARA REVISÃO.** Nada abaixo será usado na classificação
> enquanto você não aprovar. Marquei com ⚖️ os pontos que dependem de juízo
> jurídico ou de decisão sua de escopo.

## Por que uma taxonomia *consolidada* (e não uma por edital)

Extraí a taxonomia de cada um dos 5 editais separadamente (em
`config/taxonomias/{slug}.json`). Mas para o produto — comparar o *perfil
estatístico* de cada banca/cargo — os 1.072 itens precisam ser classificados
num **esquema único**. Se cada concurso usasse a própria árvore, os números
não seriam comparáveis entre anos e cargos.

Os editais do piloto descrevem quase o mesmo núcleo, com granularidades
diferentes. Comparação da riqueza da árvore por disciplina:

| Disciplina | PF Agente (18/21) | PRF (18/19/21) | DPRF 2013 |
|---|---|---|---|
| Administrativo | 8 tópicos, bem estruturado | 8 tópicos | 9 tópicos |
| Constitucional | 4 tópicos "achatados" | **5 tópicos, mais detalhado** | 8 tópicos |
| Penal | fundido com Proc. Penal | **separado, granular** | granular |

**Proposta**: usar como espinha dorsal o edital mais rico por disciplina
(PRF 2021 para Constitucional e Penal; os de Administrativo são equivalentes),
e mapear os demais sobre ele. O esquema fica em 2 níveis (**tópico → subtópico**),
como combinado na Fase 2.

---

## Decisões que preciso de você (antes de classificar)

**D1. Direito Penal e Direito Processual Penal: juntos ou separados?** ⚖️
O edital do PF Agente funde os dois numa disciplina; PRF e DPRF separam.
São campos distintos e a separação dá granularidade comercial.
→ **Recomendo separar** em duas disciplinas.

**D2. "Legislação Especial" (Lei de Drogas, Estatuto do Desarmamento, crimes
hediondos, tortura, abuso de autoridade, Maria da Penha, etc.):** disciplina
própria ou subtópicos de Penal? ⚖️ Ela cai bastante em PF/PRF e tem peso
estatístico próprio. → **Recomendo disciplina própria** ("Legislação Penal
Especial"), fora do recorte das 3 disciplinas-piloto por ora, mas já
etiquetada para não poluir Penal.

**D3. Escopo da classificação fina:** classifico só as 3 disciplinas-piloto
(Constitucional, Administrativo, Penal) no nível subtópico, e deixo o resto
(Português, Informática, RLM, etc.) apenas com rótulo de disciplina?
→ **Recomendo sim** — é onde está o valor e o que o CLAUDE.md define como piloto.

**D4. Controle de constitucionalidade** aparece no edital do Delegado (fora do
piloto), mas **não** nos editais de Agente/PRF. ⚖️ Mantenho como tópico de
Constitucional mesmo assim (pode cair como "noção"), ou removo?
→ **Recomendo manter**, marcado como "raro no piloto".

---

## Taxonomia consolidada proposta

### DIREITO CONSTITUCIONAL

1. **Teoria da Constituição e poder constituinte**
   - Conceito, classificação das constituições, elementos
   - Poder constituinte originário e derivado; reforma e revisão; emendas
   - Aplicabilidade das normas constitucionais (eficácia plena, contida, limitada)
2. **Controle de constitucionalidade** ⚖️ *(raro no piloto — ver D4)*
   - Sistemas de controle; inconstitucionalidade por ação e omissão
3. **Direitos e garantias fundamentais**
   - Direitos e deveres individuais e coletivos
   - Direito à vida, liberdade, igualdade, segurança, propriedade
   - Direitos sociais; nacionalidade; cidadania; direitos políticos; partidos
   - Remédios constitucionais (HC, MS, MI, HD, ação popular)
4. **Organização do Estado**
   - Organização político-administrativa; União, estados, DF, municípios
   - Competências (arts. 20 a 24 da CF)
   - Administração pública na CF (arts. 37 a 41)
5. **Organização dos poderes**
   - Poder Legislativo; processo legislativo
   - Poder Executivo; atribuições do presidente da República
   - Poder Judiciário; funções essenciais à justiça
6. **Defesa do Estado e das instituições democráticas**
   - Segurança pública (art. 144); organização da segurança pública
   - Atribuições constitucionais da Polícia Federal / Polícia Rodoviária Federal
7. **Ordem social**
   - Seguridade social; meio ambiente; família, criança, idoso, índio

### DIREITO ADMINISTRATIVO

1. **Regime jurídico-administrativo e princípios**
   - Conceito, fontes; princípios expressos e implícitos
2. **Organização administrativa**
   - Centralização/descentralização, concentração/desconcentração
   - Administração direta e indireta
   - Autarquias, fundações, empresas públicas, sociedades de economia mista
3. **Atos administrativos**
   - Conceito, requisitos, atributos, classificação, espécies
   - Anulação, revogação, convalidação; vícios
4. **Poderes administrativos**
   - Hierárquico, disciplinar, regulamentar, de polícia
   - Uso e abuso do poder
5. **Agentes públicos**
   - Classificação; cargo, emprego e função
   - Lei nº 8.112/1990; regime disciplinar e processo administrativo-disciplinar
   - Disposições constitucionais aplicáveis
6. **Licitações e contratos administrativos**
   - Princípios; dispensa e inexigibilidade; modalidades; tipos; procedimento
7. **Serviços públicos** ⚖️ *(presente nos editais mais completos; ver escopo)*
   - Concessão, permissão, autorização
8. **Controle da administração pública**
   - Controle interno/externo; administrativo, judicial, legislativo
   - Tribunais de contas
9. **Responsabilidade civil do Estado**
   - Responsabilidade por ato comissivo e por omissão; excludentes
10. **Improbidade administrativa** ⚖️
    - Lei nº 8.429/1992; sanções

### DIREITO PENAL

1. **Princípios e aplicação da lei penal**
   - Legalidade, anterioridade; lei penal no tempo e no espaço
   - Tempo e lugar do crime; territorialidade e extraterritorialidade
2. **Teoria do crime — fato típico**
   - Crime doloso e culposo; erro de tipo
   - Crime consumado e tentado; crime impossível
3. **Ilicitude**
   - Causas de exclusão; excesso punível
4. **Culpabilidade**
   - Imputabilidade; erro de proibição; causas de exclusão
5. **Punibilidade**
   - Causas de extinção da punibilidade
6. **Crimes contra a pessoa**
7. **Crimes contra o patrimônio**
8. **Crimes contra a fé pública**
9. **Crimes contra a Administração Pública**
10. **Outros crimes em espécie** ⚖️ *(dignidade sexual, incolumidade pública —
    aparecem no PRF; agrupar aqui ou detalhar?)*

---

## Como isso vira classificação (próximo passo, após sua aprovação)

- **Baseline por regras**: dicionário de palavras-chave e âncoras legais por
  subtópico (ex.: "art. 5º", "habeas corpus" → Constitucional/Remédios;
  "Lei 8.112", "estágio probatório" → Administrativo/Agentes públicos;
  "art. 121", "homicídio" → Penal/Crimes contra a pessoa).
- **LLM (API Anthropic)**: prompt estruturado devolvendo JSON com disciplina,
  tópico, subtópico e confiança, incluindo o **texto motivador** no contexto.
- Cada item recebe as duas classificações; divergências e baixa confiança vão
  para o **fluxo de revisão manual** (é onde entram as dúvidas jurídicas finas).
