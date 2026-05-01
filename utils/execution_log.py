import streamlit.components.v1 as components


TAG_COLORS = {
    "SYS":   "#64748b",
    "AGENT": "#0d9488",
    "TASK":  "#fbbf24",
    "RUN":   "#3b82f6",
    "LLM":   "#a855f7",
    "DONE":  "#22c55e",
    "ERROR": "#ef4444",
}


def _color(tag: str) -> str:
    return TAG_COLORS.get(tag.upper(), "#64748b")


def render_log(lines: list[dict], running: bool = False, height: int = 340):
    """
    lines: list of {"tag": "AGENT", "msg": "Parsing report..."}
    running: show blinking cursor at end
    """
    html_lines = ""
    for i, line in enumerate(lines):
        tag = line.get("tag", "SYS").upper()
        msg = line.get("msg", "")
        color = _color(tag)
        html_lines += f"""
        <div class="log-line" style="animation-delay:{i * 0.05}s;">
            <span style="color:#475569; font-size:0.7rem; margin-right:0.5rem; user-select:none;">
                {str(i+1).zfill(2)}
            </span>
            <span style="color:{color}; font-weight:500; margin-right:0.6rem;
                         font-size:0.72rem; letter-spacing:0.05em;">[{tag}]</span>
            <span style="color:#cbd5e1;">{msg}</span>
        </div>
        """

    cursor = ""
    if running:
        cursor = """
        <div class="log-line" style="margin-top:2px;">
            <span style="color:#0d9488; animation: blink 1s step-end infinite;">█</span>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background:#0d1117; border-radius:12px; overflow:hidden; }}

        .terminal-wrap {{
            background:#0d1117;
            border:1px solid #1f2937;
            border-radius:12px;
            overflow:hidden;
            font-family:'JetBrains Mono', monospace;
        }}

        .title-bar {{
            background:#1a1f2e;
            padding:0.55rem 1rem;
            display:flex;
            align-items:center;
            gap:0.5rem;
            border-bottom:1px solid #1f2937;
        }}

        .dot {{
            width:12px; height:12px; border-radius:50%;
            display:inline-block;
        }}

        .title-text {{
            color:#475569;
            font-size:0.72rem;
            margin-left:0.5rem;
            letter-spacing:0.05em;
        }}

        .log-body {{
            padding:1rem;
            height:{height - 44}px;
            overflow-y:auto;
            background:#0d1117;
        }}

        .log-body::-webkit-scrollbar {{ width:4px; }}
        .log-body::-webkit-scrollbar-track {{ background:#0d1117; }}
        .log-body::-webkit-scrollbar-thumb {{ background:#0d9488; border-radius:2px; }}

        .log-line {{
            font-size:0.82rem;
            line-height:1.7;
            opacity:0;
            animation: fadeIn 0.3s ease forwards;
        }}

        @keyframes fadeIn {{
            from {{ opacity:0; transform:translateX(-4px); }}
            to   {{ opacity:1; transform:translateX(0); }}
        }}

        @keyframes blink {{
            0%, 100% {{ opacity:1; }}
            50%       {{ opacity:0; }}
        }}
    </style>
    </head>
    <body>
    <div class="terminal-wrap">
        <div class="title-bar">
            <span class="dot" style="background:#ef4444;"></span>
            <span class="dot" style="background:#fbbf24;"></span>
            <span class="dot" style="background:#22c55e;"></span>
            <span class="title-text">ClinicalCrew — Agent Execution Log</span>
        </div>
        <div class="log-body" id="logBody">
            {html_lines}
            {cursor}
        </div>
    </div>
    <script>
        const lb = document.getElementById('logBody');
        if(lb) lb.scrollTop = lb.scrollHeight;
    </script>
    </body>
    </html>
    """
    components.html(html, height=height, scrolling=False)