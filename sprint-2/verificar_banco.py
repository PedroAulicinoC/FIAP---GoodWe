
import sqlite3
from pathlib import Path

caminho = Path(__file__).parent / "ev_chargeops.db"

if not caminho.exists():
    print("ERRO: arquivo do banco não encontrado.")
    raise SystemExit(1)

conn = sqlite3.connect(caminho)
conn.row_factory = sqlite3.Row

print(f"Banco consultado: {caminho.resolve()}")

# Verificar quantos registros existem em cada tabela
tabelas = [
    "apartamentos",
    "usuarios",
    "identificadores",
    "sessoes",
    "leituras",
    "faturas",
    "auditoria",
]

print("\n=== QUANTIDADE DE REGISTROS ===")

for tabela in tabelas:
    resultado = conn.execute(
        f"SELECT COUNT(*) AS total FROM {tabela}"
    ).fetchone()
    print(f"{tabela}: {resultado['total']}")


# Conferir as sessões importadas
print("\n=== SESSÕES DE RECARGA ===")

sessoes = conn.execute("""
    SELECT
        s.sessao_externa_id,
        u.nome AS usuario,
        a.numero AS apartamento,
        s.status,
        s.kwh_total,
        s.rfid_recebido
    FROM sessoes AS s
    LEFT JOIN identificadores AS i
        ON i.codigo_rfid = s.rfid_recebido
    LEFT JOIN usuarios AS u
        ON u.id = i.usuario_id
    LEFT JOIN apartamentos AS a
        ON a.id = u.apartamento_id
    ORDER BY s.sessao_externa_id
""").fetchall()

for sessao in sessoes:
    print(dict(sessao))

# Conferir algumas leituras de telemetria
print("\n=== ÚLTIMAS 5 LEITURAS ===")

leituras = conn.execute("""
    SELECT
        l.timestamp,
        s.sessao_externa_id,
        l.potencia_kw,
        l.energia_kwh,
        l.status
    FROM leituras AS l
    JOIN sessoes AS s ON s.id = l.sessao_id
    ORDER BY l.timestamp DESC
    LIMIT 5
""").fetchall()

for leitura in leituras:
    print(dict(leitura))

conn.close()
