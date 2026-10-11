
def smart_charging(veiculos, limite_total_kw):
    if (
        not isinstance(limite_total_kw, (int, float))
        or isinstance(limite_total_kw, bool)
        or limite_total_kw < 0
    ):
        raise ValueError(
            "O limite de potencia deve ser um numero nao negativo."
        )

    for identificador, solicitacao in veiculos.items():
        if (
            not isinstance(solicitacao, (int, float))
            or isinstance(solicitacao, bool)
            or solicitacao < 0
        ):
            raise ValueError(
                f"Solicitacao invalida para {identificador}."
            )

    alocacao = {
        veiculo: 0.0 for veiculo in veiculos
    }

    ativos = {
        veiculo
        for veiculo, potencia in veiculos.items()
        if potencia > 0
    }

    restante = float(limite_total_kw)

    while ativos and restante > 1e-9:
        parcela = restante / len(ativos)

        saturados = [
            veiculo
            for veiculo in ativos
            if veiculos[veiculo] - alocacao[veiculo]
            <= parcela + 1e-9
        ]

        if not saturados:
            for veiculo in ativos:
                alocacao[veiculo] += parcela
            restante = 0.0
        else:
            for veiculo in saturados:
                adicional = (
                    veiculos[veiculo] - alocacao[veiculo]
                )
                alocacao[veiculo] += adicional
                restante -= adicional
                ativos.remove(veiculo)

    return alocacao
