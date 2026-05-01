import streamlit as st


ACCENT = "#0d9488"
LIGHT_ACCENT = "#2dd4bf"
BG = "#0a0f0f"
CARD_BG = "#111918"
TEXT = "#e2f0ef"
DANGER = "#ef4444"
WARNING = "#fbbf24"
SUCCESS = "#22c55e"


def inject_styles():
    st.markdown(
        """
        <link href="https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
        <style>
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            background-color: #0a0f0f;
            color: #e2f0ef;
        }
        h1, h2, h3 {
            font-family: 'Syne', sans-serif !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #0d9488, #0f766e);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.6rem;
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
            font-size: 0.95rem;
            transition: all 0.2s ease;
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #0f766e, #115e59);
            transform: translateY(-1px);
        }
        .stTabs [data-baseweb="tab"] {
            font-family: 'DM Sans', sans-serif;
            font-weight: 500;
            color: #94a3b8;
        }
        .stTabs [aria-selected="true"] {
            color: #2dd4bf !important;
        }
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: #111918;
            border: 1px solid #1f2937;
            color: #e2f0ef;
            border-radius: 8px;
        }
        .stSelectbox > div > div {
            background-color: #111918;
            border: 1px solid #1f2937;
            color: #e2f0ef;
        }
        div[data-testid="stMetricValue"] {
            font-family: 'Syne', sans-serif;
            color: #2dd4bf;
        }
        .stAlert {
            border-radius: 10px;
        }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: #111918; }
        ::-webkit-scrollbar-thumb { background: #0d9488; border-radius: 3px; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def page_header(icon: str, title: str, subtitle: str):
    st.markdown(
        f"""
        <div style="padding: 2rem 0 1rem 0;">
            <div style="font-size:2.8rem; margin-bottom:0.3rem;">{icon}</div>
            <h1 style="font-family:'Syne',sans-serif; font-size:2.2rem;
                       background: linear-gradient(135deg, #2dd4bf, #0d9488);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       margin:0; padding:0;">{title}</h1>
            <p style="color:#94a3b8; font-size:1rem; margin-top:0.4rem;">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def disclaimer_banner():
    st.markdown(
        """
        <div style="background:#1a0a0a; border-left:4px solid #ef4444;
                    border-radius:8px; padding:1rem 1.2rem; margin:1rem 0;">
            <div style="color:#ef4444; font-weight:700; font-size:0.95rem;
                        font-family:'Syne',sans-serif;">
                ⚠️ CLINICAL DECISION SUPPORT TOOL — NOT A DIAGNOSTIC SYSTEM
            </div>
            <div style="color:#fca5a5; font-size:0.85rem; margin-top:0.3rem;
                        font-family:'DM Sans',sans-serif;">
                All AI-generated suggestions are for informational purposes only.
                Every output <strong>requires review and approval by a licensed physician</strong>
                before any clinical action is taken. Do not use this tool as a substitute
                for professional medical judgment.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, icon: str, color: str = "#0d9488"):
    return f"""
    <div style="background:#111918; border:1px solid #1f2937; border-radius:12px;
                padding:1.2rem; text-align:center; border-top:3px solid {color};">
        <div style="font-size:1.8rem;">{icon}</div>
        <div style="font-family:'Syne',sans-serif; font-size:1.6rem;
                    color:{color}; font-weight:800;">{value}</div>
        <div style="color:#64748b; font-size:0.8rem; margin-top:0.2rem;">{label}</div>
    </div>
    """


def badge(text: str, color: str) -> str:
    return f"""
    <span style="background:{color}22; color:{color}; border:1px solid {color}55;
                 border-radius:20px; padding:0.2rem 0.7rem; font-size:0.78rem;
                 font-family:'DM Sans',sans-serif; font-weight:500;">{text}</span>
    """


def info_card(title: str, content: str, border_color: str = "#0d9488") -> str:
    return f"""
    <div style="background:#111918; border:1px solid #1f2937;
                border-left:4px solid {border_color}; border-radius:10px;
                padding:1.2rem; margin:0.6rem 0;">
        <div style="font-family:'Syne',sans-serif; font-weight:700;
                    color:#e2f0ef; margin-bottom:0.5rem;">{title}</div>
        <div style="color:#94a3b8; font-size:0.9rem; line-height:1.6;">{content}</div>
    </div>
    """