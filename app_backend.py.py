from flask import Flask, request, jsonify
import fitz  # PyMuPDF
from transformers import pipeline

app = Flask(__name__)

# Load Hugging Face pipeline for Q&A
qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
# Load Hugging Face pipeline for text generation (quiz generation)
generator = pipeline("text-generation", model="gpt2")

uploaded_pdfs = {}

@app.route("/upload", methods=["POST"])
def upload_pdf():
    file = request.files.get("file")
    if not file:
        return "No file uploaded", 400

    pdf_bytes = file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    uploaded_pdfs[file.filename] = text
    return jsonify({"message": f"{file.filename} uploaded successfully!"})

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.json
    filename = data.get("filename")
    question = data.get("question")

    if filename not in uploaded_pdfs:
        return "PDF not found", 404

    context = uploaded_pdfs[filename]
    answer = qa_pipeline(question=question, context=context)
    return jsonify({"answer": answer['answer']})

@app.route("/generate_quiz", methods=["POST"])
def generate_quiz():
    data = request.json
    filename = data.get("filename")
    difficulty = data.get("difficulty", "Easy")

    if filename not in uploaded_pdfs:
        return "PDF not found", 404

    text = uploaded_pdfs[filename]

    # Prompt GPT-2 to generate 3 multiple choice questions
    prompt = f"Generate 3 {difficulty} level multiple choice questions (with options and answers) from the following text:\n{text}\nQuestions:"
    quiz_text = generator(prompt, max_length=400)[0]['generated_text']

    return jsonify({"difficulty": difficulty, "quiz": quiz_text})

if __name__ == "__main__":
    app.run(debug=True)
