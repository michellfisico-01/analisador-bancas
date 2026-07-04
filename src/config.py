"""Configuração central do projeto: caminhos e constantes compartilhadas."""
from pathlib import Path

# Raiz do projeto (pasta que contém src/, data/, config/)
RAIZ = Path(__file__).resolve().parent.parent

# Caminhos de dados
DIR_CONFIG = RAIZ / "config"
DIR_DATA_RAW = RAIZ / "data" / "raw"
DIR_PROVAS = DIR_DATA_RAW / "provas"
DIR_GABARITOS = DIR_DATA_RAW / "gabaritos"
DIR_EDITAIS = DIR_DATA_RAW / "editais"
DIR_PROCESSED = RAIZ / "data" / "processed"
DIR_RELATORIOS = RAIZ / "relatorios"

# Banco de dados
CAMINHO_BD = DIR_PROCESSED / "bancas.db"

# Manifesto de coleta
CAMINHO_MANIFESTO = DIR_CONFIG / "concursos.json"

# Identificação honesta nas requisições ao site da banca
USER_AGENT = "AnalisadorBancas/0.1 (pesquisa academica; contato: michellfisico@gmail.com)"

# Delay entre downloads (segundos) — respeito ao servidor da banca
DELAY_ENTRE_DOWNLOADS = 3.0
