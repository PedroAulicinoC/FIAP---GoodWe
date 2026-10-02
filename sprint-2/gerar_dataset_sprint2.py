import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion_service import GoodWeIngestionService

def gerar_base_completa():
    print("=" * 65)
    print("  EV ChargeOps - Gerador de Cenários de Teste (GoodWe HCA G2)")
    print("=" * 65)

    servico = GoodWeIngestionService(mock_mode=True)
    diretorio = os.path.dirname(os.path.abspath(__file__))

    todas_as_leituras = []

    # Cenário 1: Sessão Normal do Morador Apt 42
    print("[*] Gerando Cenário 1: Recarga Normal (Apt 42)...")
    s1 = servico.gerar_sessao_completa(
        charger_sn="GW-HCA-G2-001",
        session_id="SES-001-NORMAL",
        tag_rfid="RFID-APT-42",
        cenario="normal",
        duracao_min=60,
    )
    if s1:
        todas_as_leituras.extend(s1)

    # Cenário 2: Sessão Interrompida do Morador Apt 105
    print("[*] Gerando Cenário 2: Sessão Interrompida Prematuramente (Apt 105)...")
    s2 = servico.gerar_sessao_completa(
        charger_sn="GW-HCA-G2-001",
        session_id="SES-002-INTERRUPT",
        tag_rfid="RFID-APT-105",
        cenario="interrompido",
        duracao_min=15,
    )
    if s2:
        todas_as_leituras.extend(s2)

    # Cenário 3: Sessão com Anomalia Elétrica (para a IA do Integrante 4)
    print("[*] Gerando Cenário 3: Anomalia Elétrica (Sobrecarga/Falha)...")
    s3 = servico.gerar_sessao_completa(
        charger_sn="GW-HCA-G2-001",
        session_id="SES-003-FAULT",
        tag_rfid="RFID-APT-88",
        cenario="anomalia",
        duracao_min=45,
    )
    if s3:
        todas_as_leituras.extend(s3)

    # Exportação consolidada
    arquivo_csv = os.path.join(diretorio, "telemetria_sprint2_consolidada.csv")
    arquivo_json = os.path.join(
        diretorio, "telemetria_sprint2_consolidada.json"
    )

    servico.exportar_leituras_csv(todas_as_leituras, arquivo_csv)
    servico.exportar_sessao_json(todas_as_leituras, arquivo_json)

    print("\n[✓] Base de testes gerada com sucesso:")
    print(f"    - CSV: {arquivo_csv}")
    print(f"    - JSON: {arquivo_json}")
    print(
        f"    - Total de registros de telemetria: {len(todas_as_leituras)} pacotes."
    )

if __name__ == "__main__":
    gerar_base_completa()