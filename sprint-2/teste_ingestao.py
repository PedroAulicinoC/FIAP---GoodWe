import os
import sys
import time

# Adiciona o diretório atual ao sys.path para importação segura
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion_service import GoodWeIngestionService


def iniciar_monitoramento():
    print("=" * 60)
    print("  EV ChargeOps - Módulo de Ingestão e Exportação (GoodWe)")
    print("=" * 60)

    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    arquivo_json = os.path.join(diretorio_atual, "telemetria_sessoes.json")
    arquivo_csv = os.path.join(diretorio_atual, "telemetria_sessoes.csv")

    station_id = "STATION-FIAP-01"
    charger_sn = "GW-HCA-G2-001"

    servico = GoodWeIngestionService(mock_mode=True)
    sucesso, token = servico.autenticar("admin@condominio.com", "senha123")

    print(f"[*] Autenticado com sucesso. Token: {token}")
    print(f"[*] Monitorando carregador: {charger_sn}...\n")

    leituras_coletadas = []

    try:
        for ciclo in range(1, 6):
            dados = servico.coletar_telemetria_carregador(
                station_id=station_id, charger_sn=charger_sn
            )

            if dados is None:
                print(
                    f"[PACOTE {ciclo:02d}] [!] Falha na coleta: pacote vazio."
                )
                continue

            leituras_coletadas.append(dados)

            print(
                f"[PACOTE {ciclo:02d}] {dados['timestamp']} | Status: {dados['status']}"
            )
            print(
                f"  ├─ Tensão: {dados['telemetria']['tensao_v']} V | Corrente: {dados['telemetria']['corrente_a']} A"
            )
            print(
                f"  ├─ Potência Ativa: {dados['telemetria']['potencia_kw']} kW"
            )
            print(
                f"  ├─ Sessão ID: {dados['sessao']['session_id']} (Identificador: {dados['sessao']['tag_rfid']})"
            )
            print(
                f"  └─ Energia Total Medida: {dados['sessao']['energia_acumulada_kwh']} kWh\n"
            )

            time.sleep(1)

        print(
            "[*] Gravando dados coletados para compartilhamento com o grupo..."
        )
        if servico.exportar_sessao_json(leituras_coletadas, arquivo_json):
            print(f"  [✓] JSON gerado com sucesso: {arquivo_json}")

        if servico.exportar_leituras_csv(leituras_coletadas, arquivo_csv):
            print(f"  [✓] CSV gerado com sucesso: {arquivo_csv}")

        print(
            "\n[✓] Telemetria coletada e persistida com sucesso para a Sprint 2!"
        )

    except KeyboardInterrupt:
        print("\n[!] Monitoramento interrompido pelo operador.")


if __name__ == "__main__":
    iniciar_monitoramento()