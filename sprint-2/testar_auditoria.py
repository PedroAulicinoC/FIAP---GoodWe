
from database import Database

db = Database()

eventos = db.listar_eventos_auditoria()

if not eventos:
    print("Nenhum evento de auditoria encontrado.")
else:
    for evento in eventos:
        print(evento)
