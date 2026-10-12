"""glass.py - tema glassmorphism GoodWe eco (modo escuro fixo)."""
import base64
import streamlit as st

ACCENT = "#16A34A"

TEMA_DARK = dict(
    bg="#07191a", glow1="rgba(52,211,153,0.22)", glow2="rgba(45,212,191,0.14)",
    glass="rgba(255,255,255,0.08)", border="rgba(255,255,255,0.16)",
    shadow="rgba(0,0,0,0.45)", text="#ffffff", muted="rgba(255,255,255,0.68)",
    accent_text="#5eeaa0", grid="rgba(255,255,255,0.09)",
    colors=["#34D399", "#86EFAC", "#2DD4BF", "#A3E635", "#94A3B8"],
    paisagem=("#04120f", "#0b3b31", "#1b6b4f", "#0d3a30", "#0a2c26", "#071d1b", "#e9fff4", ".16"),
)
2
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family: 'Poppins', sans-serif; }

.stApp {
    background-image:
        radial-gradient(circle at 15% 15%, var(--glow1), transparent 45%),
        radial-gradient(circle at 85% 10%, var(--glow2), transparent 40%),
        var(--paisagem);
    background-size: 100% 100%, 100% 100%, cover;
    background-position: center, center, center bottom;
    background-repeat: no-repeat;
    background-attachment: fixed;
    background-color: var(--bg);
}
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; }

/* vidro */
[data-testid="stMetric"], [data-testid="stDataFrame"], [data-testid="stPlotlyChart"],
[data-testid="stExpander"], [data-testid="stAlert"],
[data-testid="stSidebar"] > div:first-child {
    background: var(--glass);
    backdrop-filter: blur(18px) saturate(160%);
    -webkit-backdrop-filter: blur(18px) saturate(160%);
    border: 1px solid var(--border);
    border-radius: 24px;
    box-shadow: 0 8px 32px var(--shadow), inset 0 1px 0 rgba(255,255,255,0.18);
}
[data-testid="stMetric"] { padding: 18px 22px; transition: transform .2s ease, border-color .2s ease; }
[data-testid="stMetric"]:hover { transform: translateY(-3px); border-color: #22C55E; }
[data-testid="stMetricValue"] { font-weight: 700; color: var(--accent-text); }
[data-testid="stMetricLabel"] { color: var(--muted); }
[data-testid="stPlotlyChart"], [data-testid="stDataFrame"] { padding: 10px; overflow: visible; }

/* abas em pílula */
.stTabs [data-baseweb="tab-list"] {
    gap: 6px !important; padding: 6px !important; width: fit-content !important;
    background: var(--glass) !important; backdrop-filter: blur(12px);
    border: 1px solid var(--border) !important; border-radius: 999px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 999px !important; padding: 8px 22px !important;
    height: auto !important; color: var(--muted) !important;
}
.stTabs [aria-selected="true"] { background: #16A34A !important; color: #fff !important; }
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display: none !important; }

/* botões */
.stButton > button, .stDownloadButton > button {
    background: #16A34A; color: #fff; border: none; border-radius: 999px;
    padding: 0.5rem 1.6rem; font-weight: 500;
    box-shadow: 0 6px 18px rgba(22, 163, 74, 0.35); transition: all .2s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: #22C55E; color: #fff; transform: translateY(-1px);
}

/* inputs em pílula */
[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input {
    background: var(--glass) !important; border: 1px solid var(--border) !important;
    border-radius: 999px !important; backdrop-filter: blur(10px);
}
[data-baseweb="tag"] { background: #16A34A !important; border-radius: 999px !important; }

h1, h2, h3 { color: var(--text); letter-spacing: -0.02em; font-weight: 600; }
footer { visibility: hidden; }
</style>
"""

def _paisagem(p) -> str:
    svg = f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1600 900' preserveAspectRatio='xMidYMax slice'>
<defs><linearGradient id='s' x1='0' y1='0' x2='0' y2='1'>
<stop offset='0' stop-color='{p[0]}'/><stop offset='0.6' stop-color='{p[1]}'/><stop offset='1' stop-color='{p[2]}'/>
</linearGradient></defs>
<rect width='1600' height='900' fill='url(#s)'/>
<circle cx='1220' cy='230' r='70' fill='{p[6]}' opacity='{p[7]}'/>
<path fill='{p[3]}' d='M0 580 L220 400 L380 510 L580 340 L780 530 L980 370 L1200 550 L1400 410 L1600 530 V900 H0Z'/>
<path fill='{p[4]}' d='M0 660 L180 540 L360 630 L560 500 L760 640 L980 520 L1200 650 L1420 540 L1600 630 V900 H0Z'/>
<path fill='{p[5]}' d='M0 750 L200 680 L420 740 L640 670 L880 750 L1100 690 L1340 755 L1600 700 V900 H0Z'/>
</svg>"""
    b64 = base64.b64encode(svg.encode()).decode()
    return f"url(data:image/svg+xml;base64,{b64})"

def inject_glass():
    t = TEMA_DARK
    vars_css = (
        "<style>:root{"
        f"--bg:{t['bg']};--glow1:{t['glow1']};--glow2:{t['glow2']};"
        f"--glass:{t['glass']};--border:{t['border']};--shadow:{t['shadow']};"
        f"--text:{t['text']};--muted:{t['muted']};--accent-text:{t['accent_text']};"
        f"--paisagem:{_paisagem(t['paisagem'])};"
        "}</style>"
    )
    st.markdown(vars_css + CSS, unsafe_allow_html=True)

def glass_fig(fig, height=380):
    t = TEMA_DARK
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=t["text"], family="Poppins"),
        height=height,
        margin=dict(l=10, r=10, t=50, b=60),  # <-- Aumentado de 10 para 40 para dar espaço ao título do eixo X
        colorway=t["colors"],
        xaxis=dict(gridcolor=t["grid"], zerolinecolor=t["grid"]),
        yaxis=dict(gridcolor=t["grid"], zerolinecolor=t["grid"]),
    )
    fig.update_traces(marker_color=t["colors"][0], selector=dict(type="bar"))
    fig.update_traces(line_color=t["colors"][0], selector=dict(type="scatter", mode="lines"))
    return fig