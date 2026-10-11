
import json
import sys
from pathlib import Path

PASTA_SPRINT2 = Path(__file__).resolve().parent.parent

if str(PASTA_SPRINT2) not in sys.path:
    sys.path.insert(0, str(PASTA_SPRINT2))

from motor_rateio import processar_rateio_condominio
from integracao_ia import executar_modulo_ia


def executar_sistema_integrado(
    caminho_json,
    cadastro_unidades,
    tarifa_kwh,
    custo_manutencao,
    veiculos,
    limite_total_kw
):
    # 1. Carrega os dados das recargas
    with open(caminho_json, "r", encoding="utf-8-sig") as arquivo:
        sessoes = json.load(arquivo)

    # 2. Executa o rateio dos colegas
    faturas = processar_rateio_condominio(
        sessoes_telemetria=sessoes,
        cadastro_unidades=cadastro_unidades,
        tarifa_kwh=tarifa_kwh,
        custo_fixo_manutencao_total=custo_manutencao
    )

    # 3. Executa o módulo de IA
    resultado_ia = executar_modulo_ia(
        caminho_json=caminho_json,
        veiculos=veiculos,
        limite_total_kw=limite_total_kw
    )

    # 4. Identifica sessões que precisam de revisão
    sessoes_em_revisao = set()

    for alerta in resultado_ia["anomalias"]:
        if alerta.get("session_id"):
            sessoes_em_revisao.add(alerta["session_id"])

    for alerta in resultado_ia["anomalias_curva"]:
        if alerta.get("sessao"):
            sessoes_em_revisao.add(alerta["sessao"])

    # 5. Relaciona sessões aos moradores
    rfids_em_revisao = set()

    for registro in sessoes:
        sessao = registro.get("sessao", {})

        if sessao.get("session_id") in sessoes_em_revisao:
            rfids_em_revisao.add(sessao.get("tag_rfid"))

    # 6. Acrescenta uma indicação ao relatório
    relatorio_integrado = {}

    for rfid, fatura in faturas.items():
        relatorio_integrado[rfid] = {
            **fatura,
            "status_analise_ia": (
                "REVISAR SESSAO"
                if rfid in rfids_em_revisao
                else "SEM ALERTAS DETECTADOS"
            )
        }

    return {
        "faturas": relatorio_integrado,
        "sessoes_em_revisao": sorted(sessoes_em_revisao),
        "resultado_ia": resultado_ia
    }
