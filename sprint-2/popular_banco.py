
from database import Database

db = Database()

# Moradores de exemplo.
carlos_id = db.cadastrar_usuario(
    nome="Carlos Silva",
    apartamento_numero="42",
    email="carlos@example.com"
)

mariana_id = db.cadastrar_usuario(
    nome="Mariana Souza",
    apartamento_numero="105",
    email="mariana@example.com"
)

ana_id = db.cadastrar_usuario(
    nome="Ana Clara",
    apartamento_numero="88",
    email="ana@example.com"
)

# Os códigos precisam corresponder exatamente aos RFIDs
# que aparecem nos seus dados simulados.
db.cadastrar_identificador(
    "RFID-APT-42", carlos_id
)

db.cadastrar_identificador(
    "RFID-APT-105", mariana_id
)

db.cadastrar_identificador(
    "RFID-APT-88", ana_id
)

# RFID que aparece no exemplo de teste_ingestao.py.
db.cadastrar_identificador(
    "RFID-USER-MORADOR-APT42", carlos_id
)

print("Moradores cadastrados:")
for usuario in db.listar_usuarios():
    print(usuario)
