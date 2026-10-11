
import json
from pathlib import Path
from database import Database

arquivo = Path("telemetria_sprint2_consolidada.json")

with arquivo.open("r", encoding="utf-8") as f:
    dados = json.load(f)

# O gerador atual deve produzir uma lista de leituras.
# Se o JSON tiver um objeto envolvendo a lista, ajuste
# esta linha para a chave que contém as leituras.
if not isinstance(dados, list):
    raise ValueError(
        "Esperava uma lista JSON. Confira a estrutura do arquivo."
    )

db = Database()

quantidade = db.salvar_telemetria(
    dados,
    origem="simulado"
)

print(f"Leituras novas salvas: {quantidade}")

print("\nSessões registradas:")
for sessao in db.listar_sessoes():
    print(sessao)
