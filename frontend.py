import os
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app

st.set_page_config(
    page_title="AI Travel Booking System",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --ink:        #0A0E17;
    --panel:      #12192A;
    --panel-2:    #0D1220;
    --border:     #24304A;
    --border-soft:#1A2338;
    --amber:      #E8A33D;
    --amber-dim:  rgba(232,163,61,0.16);
    --sky:        #4FB6D9;
    --coral:      #E27A54;
    --violet:     #9084D6;
    --cream:      #F3EEE2;
    --ink-text:   #E9EEF6;
    --text-2:     #93A6C2;
    --text-3:     #5C7091;
}

html, body, .stApp {
    font-family: 'Inter', sans-serif;
    background:
        radial-gradient(ellipse 900px 500px at 15% -10%, rgba(232,163,61,0.06), transparent),
        radial-gradient(ellipse 900px 600px at 100% 10%, rgba(79,182,217,0.06), transparent),
        var(--ink);
}

/* ── Hero — boarding pass header ── */
.hero-wrapper {
    position: relative;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 0;
    border: 1px solid var(--border-soft);
}
.hero-bg {
    width: 100%;
    height: 260px;
    object-fit: cover;
    object-position: center 42%;
    display: block;
    filter: brightness(0.62) saturate(1.1);
    position: absolute;
    top: 0; left: 0;
}
.hero-wrapper::before {
    content: "";
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 620px 260px at 50% 55%, rgba(10,14,23,0.72) 0%, rgba(10,14,23,0.38) 60%, rgba(10,14,23,0.12) 100%),
        linear-gradient(180deg, rgba(10,14,23,0.35) 0%, rgba(10,14,23,0.15) 40%, rgba(10,14,23,0.45) 100%);
    z-index: 1;
}
.hero-content {
    position: relative;
    z-index: 2;
    height: 260px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 1.5rem;
}
.hero-badge {
    background: var(--amber-dim);
    border: 1px solid rgba(232,163,61,0.45);
    color: #f2c777 !important;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.32rem 0.9rem;
    border-radius: 20px;
    margin-bottom: 1rem;
    display: inline-block;
}
.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 0.55rem;
    line-height: 1.15;
    letter-spacing: -0.01em;
}
.hero-sub {
    color: #c3d3e8;
    font-size: 0.98rem;
    max-width: 560px;
}

/* ── Perforated route strip beneath hero (the "ticket tear") ── */
.route-strip {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.9rem;
    background: var(--panel-2);
    border: 1px solid var(--border-soft);
    border-top: none;
    border-radius: 0 0 18px 18px;
    padding: 0.65rem 1rem;
    margin-bottom: 2rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    color: var(--text-3);
    text-transform: uppercase;
    overflow: hidden;
}
.route-strip::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background-image: repeating-linear-gradient(90deg, var(--border) 0 8px, transparent 8px 16px);
}
.route-strip .stop { color: var(--text-2); }
.route-strip .stop.active { color: var(--amber); font-weight: 600; }
.route-strip .dash { color: var(--border); }

/* ── Input card ── */
.input-label {
    color: var(--amber);
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.6rem;
}

/* ── Quick destinations — passport stamp style ── */
.stamp-wrap {
    border-radius: 50%;
    overflow: hidden;
    position: relative;
    height: 92px;
    width: 92px;
    margin: 0 auto;
    border: 2px dashed rgba(232,163,61,0.55);
    padding: 4px;
}
.stamp-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 50%;
    filter: grayscale(0.25) sepia(0.18) brightness(0.72) contrast(1.05);
}
.stamp-label {
    text-align: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.04em;
    color: var(--text-2);
    margin-top: 0.5rem;
}

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}

/* Secondary (quick-suggestion) buttons */
div[data-testid="stButton"] > button[kind="secondary"] {
    background: var(--panel) !important;
    color: var(--text-2) !important;
    border: 1px solid var(--border) !important;
    font-size: 0.82rem !important;
    padding: 0.5rem 0.8rem !important;
}
div[data-testid="stButton"] > button[kind="secondary"]:hover {
    border-color: var(--sky) !important;
    color: var(--ink-text) !important;
    background: #0F1B2C !important;
}

/* Primary (generate) button — the CTA */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #F0B24E 0%, #E8A33D 45%, #D4832B 100%) !important;
    color: #1A1204 !important;
    border: none !important;
    padding: 0.9rem 2.5rem !important;
    font-size: 1.05rem !important;
    letter-spacing: 0.02em !important;
    width: 100% !important;
    box-shadow: 0 0 26px rgba(232,163,61,0.30), 0 4px 15px rgba(0,0,0,0.4) !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    box-shadow: 0 0 42px rgba(232,163,61,0.5), 0 6px 20px rgba(0,0,0,0.5) !important;
    transform: translateY(-2px) !important;
}
div[data-testid="stButton"] > button[kind="primary"]:active {
    transform: translateY(0px) !important;
}

/* ── Agent status cards — each leg of the route gets its own accent ── */
[data-testid="stStatusWidget"] {
    background: var(--panel) !important;
    border: 1px solid var(--border-soft) !important;
    border-left: 3px solid var(--sky) !important;
    border-radius: 10px !important;
    margin-bottom: 0.6rem !important;
}
[data-testid="stStatusWidget"]:nth-of-type(1) { border-left-color: var(--sky) !important; }
[data-testid="stStatusWidget"]:nth-of-type(2) { border-left-color: var(--violet) !important; }
[data-testid="stStatusWidget"]:nth-of-type(3) { border-left-color: var(--coral) !important; }
[data-testid="stStatusWidget"]:nth-of-type(4) { border-left-color: var(--amber) !important; }
[data-testid="stStatusWidget"] > div:first-child {
    background: var(--panel) !important;
    border-radius: 9px 9px 0 0 !important;
    font-family: 'Space Grotesk', sans-serif !important;
}
[data-testid="stStatusWidget"] details,
[data-testid="stStatusWidget"] details > div,
[data-testid="stStatusWidget"] [data-testid="stVerticalBlock"] {
    background: var(--panel-2) !important;
    color: var(--ink-text) !important;
    padding: 0.25rem 0.5rem !important;
}
[data-testid="stStatusWidget"] * { color: var(--ink-text) !important; }
[data-testid="stStatusWidget"] a { color: var(--sky) !important; }
[data-testid="stStatusWidget"] hr { border-color: var(--border-soft) !important; }

/* ── Section headers ── */
.sec-head {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin: 2.2rem 0 0.9rem;
    padding-bottom: 0.55rem;
    border-bottom: 1px solid var(--border-soft);
}
.sec-head span {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--ink-text);
}

/* ── Metric strip — styled like a ticket stub summary ── */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1.5rem 0;
}
.metric-box {
    flex: 1;
    background: var(--panel);
    border: 1px solid var(--border-soft);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.metric-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--amber);
}
.metric-lbl {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    color: var(--text-2) !important;
    margin-top: 0.25rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Final plan — rendered as an actual boarding pass ── */
.ticket {
    position: relative;
    background: linear-gradient(165deg, #12192A 0%, #0D1220 100%);
    border: 1px solid var(--border-soft);
    border-radius: 16px;
    overflow: hidden;
}
.ticket-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 1.6rem;
    background: var(--amber-dim);
    border-bottom: 2px dashed rgba(232,163,61,0.4);
}
.ticket-head .tk-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #f2c777;
}
.ticket-head .tk-code {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #fff;
}
.ticket-head::before, .ticket-head::after {
    content: "";
    position: absolute;
    width: 22px; height: 22px;
    background: var(--ink);
    border-radius: 50%;
    top: calc(100% - 11px);
}
.ticket-head::before { left: -11px; }
.ticket-head::after { right: -11px; }
.ticket-body {
    padding: 1.7rem 1.8rem 1.4rem;
    line-height: 1.8;
    color: var(--cream);
    font-size: 0.95rem;
}
.ticket-barcode {
    height: 26px;
    margin: 0 1.8rem 1.5rem;
    background-image: repeating-linear-gradient(90deg,
        var(--text-3) 0px, var(--text-3) 2px,
        transparent 2px, transparent 5px,
        var(--text-3) 5px, var(--text-3) 6px,
        transparent 6px, transparent 10px);
    opacity: 0.45;
    border-radius: 2px;
}

/* ── Save bar ── */
.save-bar {
    background: var(--panel);
    border: 1px solid var(--border-soft);
    border-radius: 10px;
    padding: 0.85rem 1.2rem;
    color: #8ab8d8 !important;
    font-size: 0.88rem;
    margin-top: 0.5rem;
}
.save-bar code { color: var(--sky) !important; background: var(--panel-2) !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--panel-2) !important;
    border-right: 1px solid var(--border-soft) !important;
}
.sidebar-chip {
    background: var(--panel);
    border: 1px solid var(--border-soft);
    border-radius: 8px;
    padding: 0.45rem 0.75rem;
    margin-bottom: 0.4rem;
    font-size: 0.83rem;
    color: var(--text-2);
    font-family: 'JetBrains Mono', monospace;
}
.sidebar-title {
    font-family: 'Space Grotesk', sans-serif;
    color: var(--ink-text);
    font-size: 1rem;
    font-weight: 600;
    margin: 1.1rem 0 0.6rem;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown { color: #a0c4e0 !important; }
section[data-testid="stSidebar"] hr { border-color: var(--border-soft) !important; }

/* Hide default branding */
#MainMenu, footer, header { visibility: hidden; }

/* Textarea */
.stTextArea textarea {
    background: var(--panel-2) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 10px !important;
    color: #e8f4ff !important;
    font-size: 0.95rem !important;
    resize: none !important;
}
.stTextArea textarea:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 2px rgba(232,163,61,0.22) !important;
}
.stTextArea textarea::placeholder { color: var(--text-3) !important; }

/* Text input (sidebar User ID field) */
input[type="text"], .stTextInput input {
    background: var(--panel) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: 8px !important;
    color: var(--ink-text) !important;
}
input[type="text"]:focus, .stTextInput input:focus {
    border-color: var(--amber) !important;
    box-shadow: 0 0 0 2px rgba(232,163,61,0.22) !important;
}
input[type="text"]::placeholder { color: var(--text-3) !important; }

/* All Streamlit labels */
.stTextInput label, .stTextArea label,
.stSelectbox label, .stNumberInput label {
    color: var(--sky) !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
}

/* General markdown / paragraph text */
.stMarkdown p, .stMarkdown li, .stMarkdown td, .stMarkdown th { color: #cce0f5 !important; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #e8f4ff !important;
}
.stMarkdown code {
    background: var(--panel) !important;
    color: var(--sky) !important;
    padding: 0.15em 0.4em;
    border-radius: 4px;
}

/* Streamlit warning / info / success on dark bg */
.stAlert { background: var(--panel) !important; border-radius: 10px !important; }
.stAlert p, .stAlert div { color: var(--ink-text) !important; }

/* Download button */
div[data-testid="stDownloadButton"] > button {
    background: var(--panel) !important;
    color: var(--ink-text) !important;
    border: 1px solid var(--sky) !important;
    border-radius: 10px !important;
}
div[data-testid="stDownloadButton"] > button:hover {
    background: #0F1F2C !important;
    border-color: var(--sky) !important;
}

/* Visible keyboard focus for accessibility */
button:focus-visible, input:focus-visible, textarea:focus-visible {
    outline: 2px solid var(--amber) !important;
    outline-offset: 2px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sidebar-title'>🌍 AI Travel Planner</div>", unsafe_allow_html=True)
    st.markdown("---")

    thread_id = st.text_input("👤 User ID", value="aarohi_user",
                              help="Your session ID — keeps travel history across queries")

    st.markdown("<div class='sidebar-title'>Powered by</div>", unsafe_allow_html=True)
    for tech in ["🔗 LangGraph", "🧠 Groq · LLaMA 3.3 70B", "🐘 PostgreSQL", "🔍 Tavily Search", "✈️ AviationStack"]:
        st.markdown(f"<div class='sidebar-chip'>{tech}</div>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-title'>Agent Pipeline</div>", unsafe_allow_html=True)
    for step in ["① Flight Agent", "② Hotel Agent", "③ Itinerary Agent", "④ Final Agent"]:
        st.markdown(f"<div class='sidebar-chip'>{step}</div>", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
    <img class="hero-bg"
         src="https://images.unsplash.com/photo-1436491865332-7a61a109cc05?auto=format&fit=crop&w=1600&h=300&q=80"
         alt="airplane above clouds"/>
    <div class="hero-content">
        <div class="hero-badge">✦ Multi-Agent AI System</div>
        <div class="hero-title">✈️ AI Travel Booking System</div>
        <div class="hero-sub">Four specialized agents work together — searching flights, hotels, building an itinerary, and delivering your perfect trip plan.</div>
    </div>
</div>
<div class="route-strip">
    <span class="stop active">FLIGHTS</span><span class="dash">···</span>
    <span class="stop">HOTELS</span><span class="dash">···</span>
    <span class="stop">ITINERARY</span><span class="dash">···</span>
    <span class="stop">FINAL PLAN</span>
</div>
""", unsafe_allow_html=True)

# ── Destination image strip — passport stamps ─────────────────────────────────
DESTINATIONS = [
    ("🇯🇵 Tokyo",     "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=300&q=70"),
    ("🇫🇷 Paris",     "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=300&q=70"),
    ("🇹🇭 Bangkok",   "https://images.unsplash.com/photo-1508009603885-50cf7c579365?w=300&q=70"),
    ("🇮🇹 Rome",      "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=300&q=70"),
    ("🇦🇪 Dubai",     "https://images.unsplash.com/photo-1512453979798-5ea266f8880c?w=300&q=70"),
]

cols = st.columns(5)
for col, (name, img_url) in zip(cols, DESTINATIONS):
    with col:
        st.markdown(f"""
        <div class="stamp-wrap"><img src="{img_url}" /></div>
        <div class="stamp-label">{name}</div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Input ─────────────────────────────────────────────────────────────────────
st.markdown("<div class='input-label'>🗺️ Describe your trip</div>", unsafe_allow_html=True)

QUICK = ["7-day Japan under ₹2L", "Paris trip for 5 days", "Dubai weekend trip", "Bali backpacking 10 days"]
qcols = st.columns(len(QUICK))
quick_fill = ""
for qc, label in zip(qcols, QUICK):
    with qc:
        if st.button(label, key=f"q_{label}", type="secondary", use_container_width=True):
            quick_fill = label

user_query = st.text_area(
    "",
    value=quick_fill,
    placeholder="e.g. Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs",
    height=100,
    label_visibility="collapsed",
)

generate = st.button("🚀  Generate My Travel Plan", use_container_width=True, type="primary")

# ── Agent pipeline ────────────────────────────────────────────────────────────
AGENT_META = {
    "flight_agent":    ("✈️", "Flight Agent"),
    "hotel_agent":     ("🏨", "Hotel Agent"),
    "itinerary_agent": ("🗓️", "Itinerary Agent"),
    "final_agent":     ("🧠", "Final Agent"),
}

if generate:
    if not user_query.strip():
        st.warning("Please describe your trip first.")
    else:
        config = {"configurable": {"thread_id": thread_id}}
        collected = {"flight_results": "", "hotel_results": "",
                     "itinerary": "", "final_response": "", "llm_calls": 0}

        st.markdown("---")
        st.markdown("<div class='sec-head'><span>🤖 Agent Pipeline — Live</span></div>",
                    unsafe_allow_html=True)

        for chunk in app.stream(
            {
                "messages": [HumanMessage(content=user_query)],
                "user_query": user_query,
                "flight_results": "",
                "hotel_results": "",
                "itinerary": "",
                "llm_calls": 0,
            },
            config=config,
            stream_mode="updates",
        ):
            for node_name, state_update in chunk.items():
                icon, label = AGENT_META.get(node_name, ("🔧", node_name))

                with st.status(f"{icon}  {label}", state="complete", expanded=True):
                    if node_name == "flight_agent":
                        text = state_update.get("flight_results", "")
                        collected["flight_results"] = text
                        st.markdown(text or "_No flight data returned._")

                    elif node_name == "hotel_agent":
                        text = state_update.get("hotel_results", "")
                        collected["hotel_results"] = text
                        st.markdown(text or "_No hotel data returned._")

                    elif node_name == "itinerary_agent":
                        text = state_update.get("itinerary", "")
                        collected["itinerary"] = text
                        collected["final_response"] = text
                        st.markdown(text or "_No itinerary generated._")

                    elif node_name == "final_agent":
                        msgs = state_update.get("messages", [])
                        text = msgs[-1].content if msgs else ""
                        collected["final_response"] = text
                        st.markdown(text or "_No final response._")

                    collected["llm_calls"] = state_update.get("llm_calls", collected["llm_calls"])

        # Metrics
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-box"><div class="metric-val">4</div><div class="metric-lbl">Agents Run</div></div>
            <div class="metric-box"><div class="metric-val">{collected['llm_calls']}</div><div class="metric-lbl">LLM Calls</div></div>
            <div class="metric-box"><div class="metric-val">✅</div><div class="metric-lbl">Status</div></div>
        </div>
        """, unsafe_allow_html=True)

        # Final plan — rendered as a boarding pass
        if collected["final_response"]:
            st.markdown("<div class='sec-head'><span>🧠 Final Travel Plan</span></div>",
                        unsafe_allow_html=True)
            ticket_code = datetime.now().strftime("TRP-%y%m%d-%H%M")
            st.markdown(f"""
            <div class="ticket">
                <div class="ticket-head">
                    <span class="tk-label">Boarding Pass · Your Trip</span>
                    <span class="tk-code">{ticket_code}</span>
                </div>
                <div class="ticket-body">{collected['final_response']}</div>
                <div class="ticket-barcode"></div>
            </div>
            """, unsafe_allow_html=True)

        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"travel_plan_{timestamp}.md"
        save_dir = os.path.join(os.path.dirname(__file__), "travel_plans")
        os.makedirs(save_dir, exist_ok=True)

        file_content = f"""# Travel Plan
**Query:** {user_query}
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**User ID:** {thread_id}

---

## ✈️ Flight Information
{collected['flight_results'] or 'N/A'}

---

## 🏨 Hotel Information
{collected['hotel_results'] or 'N/A'}

---

## 🗓️ Itinerary
{collected['itinerary'] or 'N/A'}

---

## 🧠 Final Travel Plan
{collected['final_response'] or 'N/A'}

---
*LLM Calls: {collected['llm_calls']}*
"""
        with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
            f.write(file_content)

        dl_col, info_col = st.columns([1, 3])
        with dl_col:
            st.download_button("⬇️ Download Plan", data=file_content,
                               file_name=filename, mime="text/markdown",
                               use_container_width=True)
        with info_col:
            st.markdown(f"<div class='save-bar'>📁 Auto-saved → <code>travel_plans/{filename}</code></div>",
                        unsafe_allow_html=True)
