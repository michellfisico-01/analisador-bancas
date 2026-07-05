"""Schema e acesso ao banco SQLite.

O schema já nasce preparado para o produto completo: múltiplas bancas
(CEBRASPE, FGV, FCC), múltiplos formatos (certo/errado e múltipla escolha)
e a classificação de tópicos da Fase 2.
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

from src.config import CAMINHO_BD

SCHEMA = """
CREATE TABLE IF NOT EXISTS concursos (
    id        INTEGER PRIMARY KEY,
    banca     TEXT NOT NULL,              -- CEBRASPE, FGV, FCC...
    orgao     TEXT NOT NULL,              -- PF, PRF, TRT-1, RFB...
    nome      TEXT NOT NULL,              -- "PF 2021"
    ano_prova INTEGER NOT NULL,           -- ano de APLICACAO da prova
    slug      TEXT NOT NULL UNIQUE        -- identificador oficial (pf_21)
);

CREATE TABLE IF NOT EXISTS provas (
    id               INTEGER PRIMARY KEY,
    concurso_id      INTEGER NOT NULL REFERENCES concursos(id),
    cargo            TEXT NOT NULL,
    formato          TEXT NOT NULL CHECK (formato IN ('certo_errado', 'multipla_escolha')),
    arquivo_prova    TEXT,                -- caminho local do PDF do caderno
    arquivo_gabarito TEXT,                -- caminho local do PDF do gabarito definitivo
    itens_esperados  INTEGER,             -- para o relatorio de qualidade
    UNIQUE (concurso_id, cargo)
);

-- Texto motivador: bloco de contexto que antecede um grupo de itens.
-- No formato CEBRASPE o item isolado muitas vezes nao se entende sem ele.
CREATE TABLE IF NOT EXISTS textos_motivadores (
    id       INTEGER PRIMARY KEY,
    prova_id INTEGER NOT NULL REFERENCES provas(id),
    posicao  INTEGER NOT NULL,            -- ordem do bloco dentro do caderno
    texto    TEXT NOT NULL,
    UNIQUE (prova_id, posicao)
);

CREATE TABLE IF NOT EXISTS itens (
    id                  INTEGER PRIMARY KEY,
    prova_id            INTEGER NOT NULL REFERENCES provas(id),
    numero              INTEGER NOT NULL, -- numero do item no caderno
    texto               TEXT NOT NULL,
    texto_motivador_id  INTEGER REFERENCES textos_motivadores(id),
    bloco               TEXT,             -- "BLOCO I", "BLOCO II"... quando existir
    disciplina          TEXT,             -- preenchida na classificacao (Fase 2)
    gabarito            TEXT,             -- 'C'/'E' (certo/errado) ou 'A'..'E' (multipla escolha)
    status              TEXT NOT NULL DEFAULT 'valida'
                        CHECK (status IN ('valida', 'anulada', 'alterada')),
    UNIQUE (prova_id, numero)
);

-- Fase 2: cada item pode ter varias classificacoes, com origem registrada:
-- 'regras' (Camada 1), 'modelo' (Camada 2, TF-IDF local), 'manual' (revisao)
CREATE TABLE IF NOT EXISTS classificacoes (
    id         INTEGER PRIMARY KEY,
    item_id    INTEGER NOT NULL REFERENCES itens(id),
    metodo     TEXT NOT NULL CHECK (metodo IN ('regras', 'modelo', 'manual')),
    topico     TEXT NOT NULL,
    subtopico  TEXT,
    confianca  REAL,                      -- 0.0 a 1.0
    revisado   INTEGER NOT NULL DEFAULT 0,
    criado_em  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE (item_id, metodo)
);

CREATE INDEX IF NOT EXISTS idx_itens_prova ON itens(prova_id);
CREATE INDEX IF NOT EXISTS idx_class_item ON classificacoes(item_id);
"""


def conectar(caminho: Path = CAMINHO_BD) -> sqlite3.Connection:
    """Abre conexão com o banco, criando o schema se necessário."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(caminho)
    con.execute("PRAGMA foreign_keys = ON")
    _migrar(con)
    con.executescript(SCHEMA)
    return con


def _migrar(con: sqlite3.Connection) -> None:
    """Migrações de schema em bancos já existentes.

    2026-07-04 (custo zero): o metodo 'llm' saiu do CHECK de classificacoes e
    entrou 'modelo'. A tabela antiga é descartada — só continha rótulos de
    'regras', que são regenerados por ``python -m src.classificacao.regras``.
    """
    linha = con.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='classificacoes'"
    ).fetchone()
    if linha and "'llm'" in (linha[0] or ""):
        con.execute("DROP TABLE classificacoes")
        con.commit()
