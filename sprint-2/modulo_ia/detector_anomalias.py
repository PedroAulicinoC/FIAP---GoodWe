
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


def detectar_variacoes_potencia(dados, limite_variacao_pct=15):
    alertas = []

    sessoes = {}

    for registro in dados:
        sessao = registro.get("sessao", {})
        identificador = sessao.get("session_id")

        if identificador is None:
            continue

        sessoes.setdefault(identificador, []).append(registro)

    for identificador, registros in sessoes.items():
        registros = sorted(
            registros,
            key=lambda r: r.get("sessao", {}).get(
                "tempo_decorrido_minutos", 0
            )
        )

        for anterior, atual in zip(registros, registros[1:]):
            potencia_anterior = anterior.get(
                "telemetria", {}
            ).get("potencia_kw")

            potencia_atual = atual.get(
                "telemetria", {}
            ).get("potencia_kw")

            if not all(
                isinstance(valor, (int, float))
                and not isinstance(valor, bool)
                for valor in (potencia_anterior, potencia_atual)
            ):
                continue

            if potencia_anterior <= 0 or potencia_atual <= 0:
                continue

            variacao = (
                abs(potencia_atual - potencia_anterior)
                / potencia_anterior
            ) * 100

            if variacao > limite_variacao_pct:
                alertas.append({
                    "sessao": identificador,
                    "tempo_minutos": atual["sessao"].get(
                        "tempo_decorrido_minutos"
                    ),
                    "potencia_anterior_kw": potencia_anterior,
                    "potencia_atual_kw": potencia_atual,
                    "variacao_percentual": round(variacao, 2),
                    "tipo": "Variacao brusca de potencia"
                })

    return alertas
