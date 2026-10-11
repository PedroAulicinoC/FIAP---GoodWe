from pathlib import Path
from integracao_ia import executar_modulo_ia


def main():
    caminho_json = (
        Path(__file__).resolve().parent
        / "telemetria_sprint2_consolidada.json"
    )

    veiculos = {
        "Veiculo_A": 2.0,
        "Veiculo_B": 7.0,
        "Veiculo_C": 7.0
    }

    resultado = executar_modulo_ia(
        caminho_json=caminho_json,
        veiculos=veiculos,
        limite_total_kw=11.0
    )

    print("\n========== MÓDULO DE IA GOODWE ==========")
    print("Registros analisados:", resultado["registros_analisados"])
    print("Registros com alertas:", len(resultado["anomalias"]))

    print("\nALERTAS NA CURVA DE POTÊNCIA")
    print("Total:", len(resultado["anomalias_curva"]))
    for alerta in resultado["anomalias_curva"]:
        print(alerta)

    print("\nPREVISÃO EXPERIMENTAL ANTERIOR")
    print(resultado["previsao"])

    print("\nNOVA PREVISÃO POR CICLOS")
    print(resultado["previsao_ciclos"])

    print("\nSMART CHARGING")
    for veiculo, potencia in resultado["distribuicao_potencia"].items():
        print(f"{veiculo}: {potencia:.2f} kW")

    total = sum(resultado["distribuicao_potencia"].values())
    print(f"\nPotência total distribuída: {total:.2f} kW")


if __name__ == "__main__":
    main()
