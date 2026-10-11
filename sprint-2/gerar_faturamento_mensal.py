
from pathlib import Path

from database import Database
from motor_rateio import (
    carregar_sessoes_json,
    processar_rateio_condominio,
)

# Configurações do faturamento de teste
TARIFA_KWH = 0.85
CUSTO_FIXO_MANUTENCAO_TOTAL = 200.00
MES_REFERENCIA = "2026-10"

ARQUIVO_JSON = (
    Path(__file__).resolve().parent
    / "telemetria_sprint2_consolidada.json"
)


def carregar_cadastro_unidades(db):
    """Busca os moradores e seus RFID no banco de dados."""
    with db.conectar() as conn:
        registros = conn.execute("""
            SELECT
                i.codigo_rfid,
                u.nome,
                a.numero AS apartamento
            FROM identificadores i
            JOIN usuarios u ON u.id = i.usuario_id
            JOIN apartamentos a ON a.id = u.apartamento_id
            WHERE i.ativo = 1
        """).fetchall()

    cadastro = {}

    for registro in registros:
        cadastro[registro["codigo_rfid"]] = {
            "nome": registro["nome"],
            "apartamento": registro["apartamento"],
            "veiculos": [],
        }

    return cadastro


def main():
    db = Database()

    # 1. Carrega os moradores cadastrados no SQLite.
    cadastro = carregar_cadastro_unidades(db)

    if not cadastro:
        raise RuntimeError(
            "Nenhum identificador RFID ativo foi encontrado. "
            "Execute python3 popular_banco.py primeiro."
        )

    # 2. Carrega as leituras de telemetria.
    sessoes = carregar_sessoes_json(str(ARQUIVO_JSON))

    if not sessoes:
        raise RuntimeError("Nenhuma leitura de telemetria encontrada.")

    # 3. Calcula o rateio com a lógica já existente.
    relatorio = processar_rateio_condominio(
        sessoes_telemetria=sessoes,
        cadastro_unidades=cadastro,
        tarifa_kwh=TARIFA_KWH,
        custo_fixo_manutencao_total=CUSTO_FIXO_MANUTENCAO_TOTAL,
    )

    # 4. Salva cada resultado usando o método do database.py.
    quantidade = 0

    
    # Consolida o consumo por apartamento antes de salvar.
    faturas_por_apartamento = {}

    for rfid, fatura in relatorio.items():
        apartamento = fatura["apartamento"]

        if apartamento not in faturas_por_apartamento:
            faturas_por_apartamento[apartamento] = {
                "titular": fatura["titular"],
                "consumo_kwh_total": 0.0,
                "custo_energia_bruto": 0.0,
                "taxa_manutencao_rateada": 0.0,
                "valor_total_fatura": 0.0,
                "tarifa_aplicada_kwh": TARIFA_KWH,
            }

        consolidada = faturas_por_apartamento[apartamento]
        consolidada["consumo_kwh_total"] += fatura["consumo_kwh_total"]
        consolidada["custo_energia_bruto"] += fatura["custo_energia_bruto"]
        consolidada["taxa_manutencao_rateada"] += fatura["taxa_manutencao_rateada"]
        consolidada["valor_total_fatura"] += fatura["valor_total_fatura"]

    quantidade = 0

    for apartamento, fatura in faturas_por_apartamento.items():
        db.salvar_fatura(
            apartamento_numero=apartamento,
            mes_referencia=MES_REFERENCIA,
            kwh_total=fatura["consumo_kwh_total"],
            tarifa_kwh=fatura["tarifa_aplicada_kwh"],
            custo_energia=fatura["custo_energia_bruto"],
            taxa_manutencao=fatura["taxa_manutencao_rateada"],
            valor_total=fatura["valor_total_fatura"],
        )

        print(
            f"[OK] Fatura do apartamento {apartamento} "
            f"({fatura['titular']}) salva."
        )
        quantidade += 1


    # 5. Consulta as faturas gravadas no banco.
    faturas = db.listar_faturas(MES_REFERENCIA)

    total_kwh = sum(f["kwh_total"] for f in faturas)
    total_energia = sum(f["custo_energia"] for f in faturas)
    total_manutencao = sum(f["taxa_manutencao"] for f in faturas)
    total_condominio = sum(f["valor_total"] for f in faturas)

    print("\n" + "=" * 50)
    print(f"FATURAMENTO CONSOLIDADO - {MES_REFERENCIA}")
    print("=" * 50)

    for fatura in faturas:
        print(
            f"Apartamento {fatura['apartamento']} | "
            f"{fatura['kwh_total']:.2f} kWh | "
            f"Total: R$ {fatura['valor_total']:.2f}"
        )

    print("-" * 50)
    print(f"Faturas processadas nesta execução: {quantidade}")
    print(f"Consumo total:      {total_kwh:.2f} kWh")
    print(f"Custo de energia:   R$ {total_energia:.2f}")
    print(f"Taxa de manutenção: R$ {total_manutencao:.2f}")
    print(f"Total do condomínio: R$ {total_condominio:.2f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
