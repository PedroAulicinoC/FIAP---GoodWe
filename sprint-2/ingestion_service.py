import csv
from datetime import datetime
import json
import os
import random
import time

try:
    import requests
except ImportError:
    requests = None


class GoodWeIngestionService:

    def __init__(
        self,
        api_url="https://openapi.goodwe.com/api",
        token=None,
        mock_mode=True,
    ):
        """mock_mode: Se True, gera telemetria simulada do HCA G2 para testes locais.
        Se False, conecta diretamente à API SEMS Portal.
        """
        self.api_url = api_url
        self.token = token
        self.mock_mode = mock_mode

    def autenticar(self, account, password):
        """Autentica na API GoodWe OpenAPI / SEMS Portal para obter token de sessão."""
        if self.mock_mode:
            self.token = "mock_token_goodwe_fiap_2026"
            return True, self.token

        if requests is None:
            return False, "Biblioteca 'requests' não instalada."

        endpoint = f"{self.api_url}/v1/Common/CrossLogin"
        payload = {"account": account, "pwd": password}
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(
                endpoint, data=json.dumps(payload), headers=headers, timeout=10
            )
            data = response.json()
            if data.get("hasError") is False:
                self.token = data.get("data", {}).get("token")
                return True, self.token
            return False, data.get("msg")
        except Exception as e:
            return False, f"Falha de conexão: {str(e)}"

    def coletar_telemetria_carregador(self, station_id, charger_sn):
        """Coleta as métricas operacionais instantâneas do carregador HCA G2."""
        if self.mock_mode:
            return self._gerar_mock_telemetria(charger_sn)

        if requests is None:
            print("[ERRO DE INGESTÃO] Biblioteca 'requests' não instalada.")
            return None

        endpoint = f"{self.api_url}/v2/PowerStation/GetMonitorDetailBySn"
        headers = {
            "token": self.token,
            "Content-Type": "application/json",
            "language": "pt",
        }
        params = {"powerStationId": station_id, "sn": charger_sn}

        try:
            response = requests.get(
                endpoint, headers=headers, params=params, timeout=10
            )
            if response.status_code == 200:
                raw_data = response.json().get("data", {})
                return self._normalizar_payload(raw_data)
            return None
        except Exception as e:
            print(f"[ERRO DE INGESTÃO] {str(e)}")
            return None

    def _gerar_mock_telemetria(self, charger_sn):
        """Simulador de sessão de recarga pontual (padrão OCPP MeterValues.req)."""
        tensao_fase = round(random.uniform(218.0, 224.0), 2)  # Volts (V)
        corrente = round(random.uniform(30.0, 32.0), 2)  # Amperes (A)
        potencia_kw = round((tensao_fase * corrente) / 1000.0, 2)  # kW

        payload_normalizado = {
            "timestamp": datetime.now().isoformat(),
            "charger_id": charger_sn,
            "station": "FIAP - Energy Innovation Lab (Aclimação L1)",
            "status": "Charging",
            "telemetria": {
                "tensao_v": tensao_fase,
                "corrente_a": corrente,
                "potencia_kw": potencia_kw,
                "temperatura_c": round(random.uniform(35.0, 42.0), 1),
                "frequencia_hz": 60.0,
            },
            "sessao": {
                "session_id": "SES-2026-FIAP-001",
                "tag_rfid": "RFID-USER-MORADOR-APT42",
                "tempo_decorrido_minutos": random.randint(15, 120),
                "energia_acumulada_kwh": round(random.uniform(2.5, 18.0), 3),
            },
        }
        return payload_normalizado

    def _normalizar_payload(self, raw_api_data):
        """Converte a resposta crua da GoodWe no padrão único de dados consumido pelo grupo."""
        return {
            "timestamp": datetime.now().isoformat(),
            "charger_id": raw_api_data.get("sn"),
            "status": raw_api_data.get("status"),
            "telemetria": {
                "tensao_v": float(raw_api_data.get("voltage", 220.0)),
                "corrente_a": float(raw_api_data.get("current", 0.0)),
                "potencia_kw": float(raw_api_data.get("power", 0.0)) / 1000.0,
                "temperatura_c": float(raw_api_data.get("temperature", 0.0)),
            },
            "sessao": {
                "energia_acumulada_kwh": float(raw_api_data.get("eday", 0.0)),
            },
        }

    def exportar_sessao_json(self, historico_leituras, caminho_arquivo):
        """Exporta a lista de leituras de telemetria em formato JSON."""
        try:
            with open(caminho_arquivo, "w", encoding="utf-8") as arquivo_json:
                json.dump(historico_leituras, arquivo_json, indent=4)
            return True
        except Exception as e:
            print(f"[!] Erro ao salvar JSON: {e}")
            return False

    def exportar_leituras_csv(self, historico_leituras, caminho_arquivo):
        """Exporta os dados em formato tabular CSV (para BD relacional e IA)."""
        if not historico_leituras:
            return False

        colunas = [
            "timestamp",
            "charger_id",
            "status",
            "session_id",
            "tag_rfid",
            "tensao_v",
            "corrente_a",
            "potencia_kw",
            "temperatura_c",
            "frequencia_hz",
            "energia_acumulada_kwh",
        ]

        try:
            with open(
                caminho_arquivo, "w", newline="", encoding="utf-8"
            ) as arquivo_csv:
                writer = csv.DictWriter(arquivo_csv, fieldnames=colunas)
                writer.writeheader()
                for leitura in historico_leituras:
                    tele = leitura.get("telemetria", {})
                    sess = leitura.get("sessao", {})
                    linha = {
                        "timestamp": leitura.get("timestamp"),
                        "charger_id": leitura.get("charger_id"),
                        "status": leitura.get("status"),
                        "session_id": sess.get("session_id"),
                        "tag_rfid": sess.get("tag_rfid"),
                        "tensao_v": tele.get("tensao_v"),
                        "corrente_a": tele.get("corrente_a"),
                        "potencia_kw": tele.get("potencia_kw"),
                        "temperatura_c": tele.get("temperatura_c"),
                        "frequencia_hz": tele.get("frequencia_hz"),
                        "energia_acumulada_kwh": sess.get(
                            "energia_acumulada_kwh"
                        ),
                    }
                    writer.writerow(linha)
            return True
        except Exception as e:
            print(f"[!] Erro ao salvar CSV: {e}")
            return False

    def gerar_sessao_completa(
        self, charger_sn, session_id, tag_rfid, cenario="normal", duracao_min=30
    ) -> list:
        """Gera uma série temporal de medições simulando uma sessão do início ao fim.
        cenarios: 'normal', 'interrompido', 'anomalia'
        """
        historico = []
        energia_acumulada = 0.0

        passos = (
            (duracao_min // 5) if cenario != "interrompido" else 3
        )  # Interrompe rápido

        for step in range(1, passos + 1):
            if cenario == "anomalia" and step == passos - 1:
                tensao = 185.0
                corrente = 44.0
                temp = 58.5
                status = "Warning"
            else:
                tensao = round(random.uniform(218.0, 222.0), 2)
                corrente = round(random.uniform(30.0, 32.0), 2)
                temp = round(random.uniform(35.0, 40.0), 1)
                status = "Charging"

            potencia_kw = round((tensao * corrente) / 1000.0, 2)
            energia_acumulada += round(potencia_kw * (5.0 / 60.0), 3)

            leitura = {
                "timestamp": datetime.now().isoformat(),
                "charger_id": charger_sn,
                "station": "FIAP - Energy Innovation Lab (Aclimação L1)",
                "status": status,
                "cenario_teste": cenario,
                "telemetria": {
                    "tensao_v": tensao,
                    "corrente_a": corrente,
                    "potencia_kw": potencia_kw,
                    "temperatura_c": temp,
                    "frequencia_hz": 60.0,
                },
                "sessao": {
                    "session_id": session_id,
                    "tag_rfid": tag_rfid,
                    "tempo_decorrido_minutos": step * 5,
                    "energia_acumulada_kwh": round(energia_acumulada, 3),
                },
            }
            historico.append(leitura)

        # Atualização do status final após a conclusão do loop (fora do for)
        if historico:
            if cenario == "interrompido":
                historico[-1]["status"] = "Aborted"
            elif cenario == "anomalia":
                historico[-1]["status"] = "Fault"
            else:
                historico[-1]["status"] = "Finished"

        return historico