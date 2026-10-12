"""EV ChargeOps - painel do gestor predial (Streamlit)."""
import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from glass import glass_fig, inject_glass

DB_PATH = Path(__file__).parent / "ev_chargeops.db"  # use uma cópia (ex.: ev_chargeops_demo.db) na demo

st.set_page_config(page_title="EV ChargeOps", page_icon="⚡", layout="wide")
inject_glass()

STATUS_CORES = {
    "Finished": "#22C55E",
    "Charging": "#38BDF8",
    "Aborted": "#FBBF24",
    "Fault": "#F43F5E",
}


# ---------- acesso a dados (somente leitura) ----------
@st.cache_data(ttl=30)
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    # mode=ro garante que o painel nunca altere o banco
    with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as con:
        return pd.read_sql_query(sql, con, params=params)


def brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


if not DB_PATH.exists():
    st.error(f"Banco não encontrado em {DB_PATH}. Rode os scripts da Sprint 2 primeiro.")
    st.stop()

# ---------- cabeçalho ----------
st.title(" EV ChargeOps")
st.caption("Gestão e rateio de recarga de veículos elétricos · GoodWe HCA G2 · REN ANEEL 1.000/2021")

meses_df = query("SELECT DISTINCT mes_referencia FROM faturas ORDER BY 1 DESC")
if meses_df.empty:
    st.warning("Nenhuma fatura no banco ainda. Rode `gerar_faturamento_mensal.py`.")
    st.stop()

sel_col, _ = st.columns([1, 3])
mes = sel_col.selectbox("Mês de referência", meses_df["mes_referencia"], help="Afeta Visão geral e Faturas")

SQL_FATURAS = """
    SELECT a.numero AS apartamento, f.kwh_total, f.tarifa_kwh, f.custo_energia,
           f.taxa_manutencao, f.valor_total, f.status
    FROM faturas f JOIN apartamentos a ON a.id = f.apartamento_id
    WHERE f.mes_referencia = ? ORDER BY a.numero
"""
SQL_SESSOES = """
    SELECT s.id, s.sessao_externa_id, s.carregador_sn, s.rfid_recebido,
           COALESCE(u.nome, '—') AS morador, COALESCE(a.numero, '—') AS apartamento,
           s.inicio, s.fim, s.status, s.kwh_total, s.origem
    FROM sessoes s
    LEFT JOIN identificadores i ON i.id = s.identificador_id
    LEFT JOIN usuarios u ON u.id = i.usuario_id
    LEFT JOIN apartamentos a ON a.id = u.apartamento_id
    ORDER BY s.inicio DESC
"""

faturas = query(SQL_FATURAS, (mes,))
sessoes = query(SQL_SESSOES)

aba1, aba2, aba3, aba4 = st.tabs(["Visão geral", "Faturas", "Sessões e telemetria", "Auditoria"])

# ---------- 1. Visão geral ----------
with aba1:
    isentos = int((faturas["valor_total"] == 0).sum())
    interrompidas = int((sessoes["status"] == "Aborted").sum())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total faturado", brl(faturas["valor_total"].sum()))
    c2.metric("Energia no mês", f"{faturas['kwh_total'].sum():,.1f} kWh")
    c3.metric("Sessões registradas", len(sessoes), f"{interrompidas} interrompidas", delta_color="off", delta_arrow="off")
    c4.metric("Apartamentos isentos", isentos)

    col_a, col_b = st.columns([3, 2])
    with col_a:
        fig = px.bar(faturas.assign(apartamento=faturas["apartamento"].astype(str)),
                     x="apartamento", y="kwh_total", text_auto=".2f",
                     labels={"apartamento": "Apartamento", "kwh_total": "kWh"},
                     title=f"Consumo por apartamento · {mes}")
        # número do apto é texto: força eixo categórico (senão o Plotly cria escala 40, 50, 60...)
        fig.update_xaxes(type="category")
        fig.update_traces(textposition="outside", cliponaxis=False)

        # Oculta a legenda redundante
        fig.update_layout(showlegend=False)

        st.plotly_chart(glass_fig(fig), width="stretch", theme=None)

        
    with col_b:
        por_status = sessoes["status"].fillna("Sem status").value_counts().reset_index()
        por_status.columns = ["status", "sessoes"]
        fig = px.pie(por_status, names="status", values="sessoes", hole=0.55,
                     color="status", color_discrete_map=STATUS_CORES,
                     title="Sessões por status")
        fig = glass_fig(fig)
        fig.update_layout(legend=dict(orientation="h", x=0.5, xanchor="center", y=-0.02),
                          margin=dict(l=10, r=10, t=50, b=50))
        fig.update_traces(textfont_color="#ffffff")
        st.plotly_chart(fig, width="stretch", theme=None)

# ---------- 2. Faturas ----------
with aba2:
    st.subheader(f"Extrato por unidade · {mes}")
    if faturas.empty:
        st.info("Sem faturas para este mês.")
    else:
        # destaca visualmente os isentos
        faturas_view = faturas.assign(
            situacao=faturas["valor_total"].apply(lambda v: "Isento" if v == 0 else "Cobrado")
        )
        st.dataframe(
            faturas_view,
            width="stretch",
            hide_index=True,
            column_config={
                "apartamento": "Apto",
                "kwh_total": st.column_config.NumberColumn("kWh", format="%.2f"),
                "tarifa_kwh": st.column_config.NumberColumn("Tarifa (R$/kWh)", format="%.4f"),
                "custo_energia": st.column_config.NumberColumn("Energia (R$)", format="%.2f"),
                "taxa_manutencao": st.column_config.NumberColumn("Manutenção (R$)", format="%.2f"),
                "valor_total": st.column_config.NumberColumn("Total (R$)", format="%.2f"),
                "status": "Status",
                "situacao": "Situação",
            },
        )
        st.download_button("⬇ Baixar CSV", faturas_view.to_csv(index=False).encode("utf-8"),
                           file_name=f"faturas_{mes}.csv", mime="text/csv")
        st.caption("Fatura = (kWh × Tarifa) + Taxa de manutenção. "
                   "Moradores sem recarga no mês ficam isentos de energia e de taxa fixa.")

# ---------- 3. Sessões e telemetria ----------
with aba3:
    st.subheader("Sessões de recarga")
    status_opts = sorted(sessoes["status"].dropna().unique())
    filtro = st.multiselect("Filtrar por status", status_opts, default=status_opts)
    sess_f = sessoes[sessoes["status"].isin(filtro)] if filtro else sessoes

    st.dataframe(
        sess_f.drop(columns=["id"]),
        width="stretch",
        hide_index=True,
        column_config={"kwh_total": st.column_config.NumberColumn("kWh", format="%.2f")},
    )
    st.caption("⚠ Horários de início/fim das sessões simuladas ainda estão em validação; "
               "evite usá-los para inferir duração.")

    if sess_f.empty:
        st.info("Nenhuma sessão com esse filtro.")
    else:
        st.subheader("Telemetria da sessão")
        rotulos = {
            int(r.id): f"#{r.id} · Apto {r.apartamento} · {r.status} · {r.kwh_total:.2f} kWh"
            for r in sess_f.itertuples()
        }
        sid = st.selectbox("Escolha uma sessão", list(rotulos), format_func=rotulos.get)

        lei = query("""SELECT timestamp, tensao_v, corrente_a, potencia_kw, energia_kwh
                       FROM leituras WHERE sessao_id = ? ORDER BY timestamp""", (sid,))
        sel = sess_f[sess_f["id"] == sid].iloc[0]

        if sel["status"] == "Aborted":
            st.warning("Sessão interrompida: cobrança proporcional ao kWh medido até o encerramento.")
        elif sel["status"] == "Fault":
            st.error("Sessão com falha reportada pelo carregador.")

        if lei.empty:
            st.info("Esta sessão não tem leituras de telemetria.")
        else:
            lei["timestamp"] = pd.to_datetime(lei["timestamp"], errors="coerce")

            # heurística simples de anomalia (não é o modelo de IA do grupo)
            med_v, med_p = lei["tensao_v"].median(), lei["potencia_kw"].median()
            anom = pd.Series(False, index=lei.index)
            if pd.notna(med_v) and med_v:
                anom |= (lei["tensao_v"] - med_v).abs() / med_v > 0.15
            if pd.notna(med_p) and med_p:
                anom |= lei["potencia_kw"] > 1.5 * med_p
            if anom.any():
                st.warning(f"{int(anom.sum())} leitura(s) com valores atípicos (heurística: tensão ±15% "
                           "da mediana ou potência >1,5× a mediana).")

            graficos = [("potencia_kw", "Potência ativa (kW)"), ("tensao_v", "Tensão (V)"),
                        ("corrente_a", "Corrente (A)"), ("energia_kwh", "Energia acumulada (kWh)")]
            cols = st.columns(2)
            for i, (campo, titulo) in enumerate(graficos):
                fig = px.line(lei, x="timestamp", y=campo, title=titulo,
                              labels={"timestamp": "", campo: ""})
                if campo in ("potencia_kw", "tensao_v") and anom.any():
                    pts = lei[anom]
                    fig.add_scatter(x=pts["timestamp"], y=pts[campo], mode="markers",
                                    marker=dict(color="#F43F5E", size=9), name="Atípico")
                with cols[i % 2]:
                    st.plotly_chart(glass_fig(fig, height=300), width="stretch", theme=None)

# ---------- 4. Auditoria ----------
with aba4:
    st.subheader("Trilha de auditoria")
    aud = query("SELECT data_hora, acao, entidade, entidade_id, detalhes "
                "FROM auditoria ORDER BY data_hora DESC LIMIT 1000")
    if aud.empty:
        st.info("Nenhum evento registrado.")
    else:
        f1, f2 = st.columns(2)
        acoes = f1.multiselect("Ação", sorted(aud["acao"].unique()))
        ents = f2.multiselect("Entidade", sorted(aud["entidade"].unique()))
        if acoes:
            aud = aud[aud["acao"].isin(acoes)]
        if ents:
            aud = aud[aud["entidade"].isin(ents)]
        st.dataframe(aud, width="stretch", hide_index=True)
        st.caption(f"{len(aud)} evento(s) exibido(s) (máx. 1000 mais recentes).")