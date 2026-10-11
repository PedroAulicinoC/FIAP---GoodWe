
from sklearn.linear_model import LinearRegression


def prever_energia(dados, tempo_minutos=30):
    if (
        not isinstance(tempo_minutos, (int, float))
        or isinstance(tempo_minutos, bool)
        or tempo_minutos < 0
    ):
        raise ValueError("O tempo deve ser um número não negativo.")

    tempos = []
    energias = []

    for registro in dados:
        sessao = registro.get("sessao", {})
        tempo = sessao.get("tempo_decorrido_minutos")
        energia = sessao.get("energia_acumulada_kwh")

        if (
            isinstance(tempo, (int, float))
            and not isinstance(tempo, bool)
            and isinstance(energia, (int, float))
            and not isinstance(energia, bool)
        ):
            tempos.append([tempo])
            energias.append(energia)

    if len(tempos) < 2:
        raise ValueError(
            "Sao necessarios pelo menos dois registros validos."
        )

    modelo = LinearRegression()
    modelo.fit(tempos, energias)

    energia_prevista = modelo.predict([[tempo_minutos]])[0]

    return {
        "tempo_minutos": tempo_minutos,
        "energia_estimada_kwh": round(
            float(energia_prevista), 3
        ),
        "observacao": (
            "Estimativa experimental; nao representa "
            "uma previsao validada de demanda futura."
        ),
    }
