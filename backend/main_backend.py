import os
import torch
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from transformers import T5Tokenizer, T5ForConditionalGeneration
from hand_to_text import describe_image_with_gpt4, clean_extracted_text

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Flask setup
app = Flask(__name__)
CORS(app)  # Enables access from React frontend
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load model and tokenizer
model_dir = "finetuned_flan_t5_flashcards_v2"
tokenizer = T5Tokenizer.from_pretrained(model_dir)
model = T5ForConditionalGeneration.from_pretrained(model_dir)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_flashcard(note_text, max_length=256):
    encoding = tokenizer(note_text, return_tensors="pt", padding="max_length",
                         truncation=True, max_length=max_length)
    input_ids = encoding["input_ids"].to(device)
    attention_mask = encoding["attention_mask"].to(device)

    output = model.generate(input_ids=input_ids, attention_mask=attention_mask, max_length=64)
    decoded = tokenizer.decode(output[0], skip_special_tokens=True)
    return decoded.strip()

def split_into_note_sections(text):
    lines = text.splitlines()
    sections = []
    current_section = ""
    for line in lines:
        line = line.strip()
        if not line:
            if current_section:
                sections.append(current_section.strip())
                current_section = ""
            continue
        if line.startswith(("-", "•")) or (line[:2].isdigit() and line[2:3] in [".", ")"]):
            if current_section:
                sections.append(current_section.strip())
            current_section = line.lstrip("-• 0123456789.() ")
        else:
            current_section += " " + line
    if current_section:
        sections.append(current_section.strip())
    return sections

# API Routes

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(filepath)
        return jsonify({'filename': filename})
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/review/<filename>', methods=['GET'])
def review_notes(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        raw_text = describe_image_with_gpt4(filepath)
        cleaned_text = clean_extracted_text(raw_text)
        return jsonify({'notes': cleaned_text})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate/<filename>', methods=['GET'])
def generate_flashcards(filename):
    text_override = request.args.get('text')
    if text_override:
        cleaned_text = text_override
    else:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        raw_text = describe_image_with_gpt4(filepath)
        cleaned_text = clean_extracted_text(raw_text)

    sections = split_into_note_sections(cleaned_text)
    flashcards = []
    for note in sections:
        qa = generate_flashcard(note)
        if qa.startswith("Q:") and "A:" in qa:
            q = qa.split("Q:", 1)[1].split("A:", 1)[0].strip()
            a = qa.split("A:", 1)[1].strip()
            flashcards.append({"question": q, "answer": a})
    return jsonify({'flashcards': flashcards})

if __name__ == '__main__':
    app.run(debug=True)
