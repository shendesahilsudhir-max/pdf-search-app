import streamlit as st
import os
from PyPDF2 import PdfReader
import base64
import re

st.set_page_config(layout="wide")

# ---------- MODE SELECTION ----------
mode = st.radio(
    "Select Mode",
    ["🔍 Smart Search", "🧠 Decision Support System"],
    horizontal=True
)

# ---------- PDF VIEW ----------
def display_pdf(file_path, page_num):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")

    pdf_display = f"""
    <iframe src="data:application/pdf;base64,{base64_pdf}#page={page_num}" 
    width="100%" height="800px"></iframe>
    """
    st.markdown(pdf_display, unsafe_allow_html=True)

# ---------- HIGHLIGHT FUNCTION ----------
def highlight_text(text, keyword):
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(
        lambda match: f"<span style='background-color:yellow;color:black'>{match.group()}</span>",
        text
    )

# =========================
# 🔍 MODE 1: SMART SEARCH
# =========================
if mode == "🔍 Smart Search":

    st.markdown("<h1 style='text-align:center;'>📘 IRC Code Search</h1>", unsafe_allow_html=True)

    # ---------- AUTO DETECT IRC CODES ----------
    pdf_files = os.listdir("pdfs")

    available_codes = []

    for file in pdf_files:
        match = re.search(r'\d{2,3}', file)  # auto-detect numbers
        if match:
            available_codes.append(match.group())

    available_codes = sorted(list(set(available_codes)))

    # ---------- SIDEBAR FILTER ----------
    st.sidebar.header("📂 Filters")

    irc_filter = st.sidebar.radio(
        "IRC Code",
        ["All"] + available_codes
    )

    query = st.text_input("🔍 Search IRC PDFs...")

    # ---------- SEARCH FUNCTION ----------
    def search_pdfs(keyword):
        results = []
        folder = "pdfs"

        for file in os.listdir(folder):
            if file.endswith(".pdf"):

                # Apply IRC filter
                if irc_filter != "All":
                    match = re.search(r'\d{2,3}', file)
                    if not match or match.group() != irc_filter:
                        continue

                reader = PdfReader(os.path.join(folder, file))

                for page_num, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and keyword.lower() in text.lower():

                        preview = text[:300]

                        results.append({
                            "file": file,
                            "page": page_num + 1,
                            "line": preview
                        })

        return results

    col1, col2 = st.columns([1, 2])

    selected_pdf = None
    selected_page = None

    if query:
        found = search_pdfs(query)

        with col1:
            st.markdown(f"### 🔎 Results ({len(found)})")

            for i, item in enumerate(found):

                code_match = re.search(r'\d{2,3}', item['file'])
                code = code_match.group() if code_match else "?"

                if st.button(
                    f"📄 IRC {code} (Page {item['page']})",
                    key=f"search_{i}"
                ):
                    selected_pdf = item["file"]
                    selected_page = item["page"]

                highlighted = highlight_text(item["line"], query)

                st.markdown(highlighted, unsafe_allow_html=True)
                st.markdown("---")

        with col2:
            if selected_pdf:
                file_path = os.path.join("pdfs", selected_pdf)
                display_pdf(file_path, selected_page)
            else:
                st.info("Select a result")

# =========================
# 🧠 MODE 2: DECISION SYSTEM
# =========================
else:

    st.markdown("<h1 style='text-align:center;'>🧠 IRC Decision Support System</h1>", unsafe_allow_html=True)

    st.sidebar.header("🎛️ Filters")

    road = st.sidebar.selectbox("Road Type", ["All", "NH", "Urban"])
    speed = st.sidebar.selectbox("Speed (km/h)", ["All", "40", "60", "80"])
    terrain = st.sidebar.selectbox("Terrain", ["All", "Plain", "Hilly"])

    query = st.text_input("Search element (e.g., zebra crossing)")

    irc_data = [
        {"name": "Zebra Crossing", "code": "IRC 67", "keywords": ["zebra","pedestrian"], "road":"Urban","speed":"40","terrain":"Plain"},
        {"name": "Speed Breaker", "code": "IRC 99", "keywords": ["speed","breaker"], "road":"Urban","speed":"40","terrain":"Plain"},
        {"name": "Crash Barrier", "code": "IRC 35", "keywords": ["barrier","guardrail"], "road":"NH","speed":"80","terrain":"Hilly"},
    ]

    def smart_search(q):
        results = []
        for item in irc_data:
            if any(word in q.lower() for word in item["keywords"]):
                results.append(item)
        return results

    def apply_filters(results):
        filtered = []
        for item in results:
            if road != "All" and item["road"] != road:
                continue
            if speed != "All" and item["speed"] != speed:
                continue
            if terrain != "All" and item["terrain"] != terrain:
                continue
            filtered.append(item)
        return filtered

    if query:
        results = apply_filters(smart_search(query))

        for item in results:
            st.markdown(f"""
            <div style="background:white;padding:15px;border-radius:10px;margin-bottom:10px;">
            <b>{item['name']}</b><br>
            📘 {item['code']}<br>
            🚧 {item['road']} | {item['speed']} km/h | {item['terrain']}
            </div>
            """, unsafe_allow_html=True)
