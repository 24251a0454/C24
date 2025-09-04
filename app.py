import streamlit as st
import requests

st.set_page_config(page_title="📘 StudyMate Prototype", layout="wide")

st.title("📘 StudyMate Prototype")

# --- Upload PDF ---
uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
pdf_filename = None

if uploaded_file:
    files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
    response = requests.post("http://127.0.0.1:5000/upload", files=files)
    if response.status_code == 200:
        st.success("PDF uploaded successfully!")
        pdf_filename = uploaded_file.name
    else:
        st.error("Failed to upload PDF")

# --- Choose Action ---
if pdf_filename:
    action = st.radio("Choose an action:", ["Get Answer", "Generate Quiz"])

    if action == "Get Answer":
        question = st.text_input("Ask a question about your PDF:")
        use_external = st.checkbox("Include external references", value=True)

        if st.button("Submit Question"):
            if question.strip() == "":
                st.warning("Please enter a question!")
            else:
                data = {"question": question, "filename": pdf_filename, "use_external": use_external}
                resp = requests.post("http://127.0.0.1:5000/ask", json=data)
                if resp.status_code == 200:
                    st.markdown(resp.json().get("answer", "No answer received"), unsafe_allow_html=True)
                else:
                    st.error("Error getting answer from backend")

    elif action == "Generate Quiz":
        difficulty = st.selectbox("Select quiz difficulty:", ["Easy", "Medium", "Hard"])
        if st.button("Generate Quiz"):
            data = {"question": "generate quiz", "filename": pdf_filename, "difficulty": difficulty}
            resp = requests.post("http://127.0.0.1:5000/ask", json=data)
            if resp.status_code == 200:
                quiz_text = resp.json().get("answer", "")
                st.markdown("### 📝 Quiz Generated:")
                st.text(quiz_text)
            else:
                st.error("Error generating quiz")

