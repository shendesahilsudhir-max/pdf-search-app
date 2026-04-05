import streamlit as st
import os
from PyPDF2 import PdfReader

# ---------------- UI STYLE ---------------- #
st.markdown("""
<style>
.main {
    text-align: center;
}
.title {
    font-size: 48px;
    font-weight: bold;
    margin-top: 100px;
}
.search-box {
    margin-top: 30px;
}
.result-box {
    text-align: left;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #
st.markdown('<div class="title">🔍 IRC CODE Search</div>', unsafe_allow_html=True)

# ---------------- SEARCH BAR ---------------- #
query = st.text_input("", placeholder="Search anything inside PDFs...")

# ---------------- SEARCH FUNCTION ---------------- #
def search_pdfs(keyword):
    results = []
    folder = "pdfs"

    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            reader = PdfReader(os.path.join(folder, file))

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    lines = text.split("\n")

                    for line in lines:
                        if keyword.lower() in line.lower():
                            results.append({
                                "file": file,
                                "page": page_num + 1,
                                "line": line
                            })

    return results

# ---------------- RESULTS ---------------- #
if query:
    found = search_pdfs(query)

    st.markdown('<div class="result-box">', unsafe_allow_html=True)

    if found:
        for item in found:
            st.markdown(f"""
            <div style="margin-bottom:20px;">
                <b>{item['file']}</b><br>
                <span style="color:gray;">Page {item['page']}</span><br>
                {item['line']}
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No results found")

    st.markdown('</div>', unsafe_allow_html=True)