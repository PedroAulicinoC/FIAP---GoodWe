
def detectar_anomalias(registro):
    alertas = []
    telemetria = registro.get("telemetria", {})
    status = registro.get("status", "Desconhecido")

    campos = [
        "tensao_v",
        "corrente_a",
        "potencia_kw",
        "temperatura_c"
    ]

    for campo in campos:
        if campo not in telemetria:
            alertas.append(f"Dado ausente: {campo}")
        elif (
            not isinstance(telemetria[campo], (int, float))
            or isinstance(telemetria[campo], bool)
        ):
            alertas.append(f"Dado invalido: {campo}")

    if alertas:
        return alertas

    tensao = telemetria["tensao_v"]
    corrente = telemetria["corrente_a"]
    potencia = telemetria["potencia_kw"]
    temperatura = telemetria["temperatura_c"]

    if tensao < 200 or tensao > 240:
        alertas.append(
            f"Tensao fora da faixa de teste: {tensao} V"
        )

    if corrente < 0 or corrente > 32:
        alertas.append(
            f"Corrente fora da faixa de teste: {corrente} A"
        )

    if potencia < 0 or potencia > 7.4:
        alertas.append(
            f"Potencia fora da faixa de teste: {potencia} kW"
        )

    if temperatura < -20 or temperatura > 50:
        alertas.append(
            f"Temperatura fora da faixa de teste: {temperatura} °C"
        )

    if status in ("Warning", "Fault"):
        alertas.append(
            f"Estado reportado pelo carregador: {status}"
        )

    return alertas
