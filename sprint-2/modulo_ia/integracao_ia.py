
import json
from pathlib import Path

from detector_anomalias import detectar_anomalias
from previsao_demanda import prever_energia
from smart_charging import smart_charging


def executar_modulo_ia(caminho_json, veiculos, limite_total_kw):
    caminho = Path(caminho_json)

    with caminho.open("r", encoding="utf-8-sig") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("O JSON deve conter uma lista de registros.")

    # 1. Detecção de anomalias
    alertas_encontrados = []

    for registro in dados:
        alertas = detectar_anomalias(registro)

        if alertas:
            alertas_encontrados.append({
                "charger_id": registro.get("charger_id"),
                "alertas": alertas
            })

    # 2. Previsão experimental de energia
    previsao = prever_energia(
        dados,
        tempo_minutos=30
    )

    # 3. Smart Charging
    distribuicao = smart_charging(
        veiculos,
        limite_total_kw
    )

    # 4. Retornar os resultados
    return {
        "registros_analisados": len(dados),
        "anomalias": alertas_encontrados,
        "previsao": previsao,
        "distribuicao_potencia": distribuicao
    }
