
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



def prever_demanda_por_ciclos(dados, duracao_futura_minutos=30):
    import pandas as pd
    from sklearn.linear_model import LinearRegression

    if duracao_futura_minutos <= 0:
        raise ValueError("A duração deve ser maior que zero.")

    registros = []

    for registro in dados:
        sessao = registro.get("sessao", {})

        if sessao.get("session_id") is not None:
            registros.append({
                "session_id": sessao.get("session_id"),
                "duracao": sessao.get("tempo_decorrido_minutos"),
                "energia": sessao.get("energia_acumulada_kwh")
            })

    df = pd.DataFrame(registros)

    if df.empty:
        raise ValueError("Nenhuma sessão encontrada.")

    resumo = df.groupby("session_id").agg(
        duracao=("duracao", "max"),
        energia=("energia", "max")
    ).dropna()

    if len(resumo) < 2:
        raise ValueError("São necessárias pelo menos duas sessões.")

    X = resumo[["duracao"]].values
    y = resumo["energia"].values

    modelo = LinearRegression()
    modelo.fit(X, y)

    previsao = modelo.predict(
        pd.DataFrame(
            {"duracao": [duracao_futura_minutos]}
        ).values
    )[0]

    return {
        "sessoes_utilizadas": len(resumo),
        "duracao_prevista_minutos": duracao_futura_minutos,
        "energia_estimada_kwh": round(max(0, float(previsao)), 3),
        "modelo": "Regressão Linear por Ciclos",
        "observacao": "Estimativa experimental com histórico limitado."
    }
