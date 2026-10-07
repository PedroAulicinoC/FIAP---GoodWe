from motor_rateio import (
    carregar_sessoes_json,
    exibir_extrato_unidade,
    processar_rateio_condominio
)

# Cadastro de unidades do condomínio (morador, apartamento, veículos e Tag RFID):
CADASTRO_UNIDADES = {
    "RFID-APT-42": {
        "nome": "Carlos Silva",
        "apartamento": "Apt 42",
        "veiculos": ["ABC-1234 (BYD Dolphin)"]
    },
    "RFID-APT-105": {
        "nome": "Mariana Souza",
        "apartamento": "Apt 105",
        "veiculos": ["XYZ-9876 (GWM Ora 3)"]
    },
    "RFID-APT-88": {
        "nome": "Ana Clara",
        "apartamento": "Apt 88",
        "veiculos": ["JKL-5544 (Volvo EX30)"]
    },
    "RFID-APT-201": {
        "nome": "João Pedro",
        "apartamento": "Apt 201",
        "veiculos": []
    }
}

# Parâmetros Financeiros de Faturamento:
TARIFA_KWH = 0.85
CUSTO_FIXO_MANUTENCAO_TOTAL = 200.0

# Carrega a base de dados de telemetria, executa a função principal do motor de rateio
# e imprime no console os extratos formatados:
if __name__ == "__main__":
    SESSOES_TELEMETRIA = carregar_sessoes_json("telemetria_sprint2_consolidada.json")

    faturas = processar_rateio_condominio(
        sessoes_telemetria=SESSOES_TELEMETRIA,
        cadastro_unidades=CADASTRO_UNIDADES,
        tarifa_kwh=TARIFA_KWH,
        custo_fixo_manutencao_total=CUSTO_FIXO_MANUTENCAO_TOTAL
    )

    for tag_rfid, fatura in faturas.items():
        exibir_extrato_unidade(fatura, tag_rfid)
        print("\n")