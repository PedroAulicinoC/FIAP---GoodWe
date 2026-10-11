import json
from pathlib import Path

from detector_anomalias import detectar_anomalias, detectar_variacoes_potencia
from previsao_demanda import prever_energia, prever_demanda_por_ciclos
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
                "session_id": registro.get("sessao", {}).get("session_id"),
                "tag_rfid": registro.get("sessao", {}).get("tag_rfid"),
                "alertas": alertas
            })

    alertas_curva = detectar_variacoes_potencia(dados)

    # 2. Previsão experimental anterior
    previsao = prever_energia(
        dados,
        tempo_minutos=30
    )

    # 3. Nova previsão por ciclos de recarga
    previsao_ciclos = prever_demanda_por_ciclos(
        dados,
        duracao_futura_minutos=30
    )

    # 4. Smart Charging
    distribuicao = smart_charging(
        veiculos,
        limite_total_kw
    )

    # 5. Retornar os resultados
    return {
        "registros_analisados": len(dados),
        "anomalias": alertas_encontrados,
        "anomalias_curva": alertas_curva,
        "previsao": previsao,
        "previsao_ciclos": previsao_ciclos,
        "distribuicao_potencia": distribuicao
    }
