# Flask-based deployment for your flashcard generation GUI as a web app

import os
import json
import torch
from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from transformers import T5Tokenizer, T5ForConditionalGeneration
from hand_to_text import describe_image_with_gpt4, clean_extracted_text

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

# Flask setup
app = Flask(__name__)
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

# Routes
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('review_notes', filename=filename))
    return render_template('upload.html')

@app.route('/review/<filename>', methods=['GET', 'POST'])
def review_notes(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if request.method == 'POST':
        edited_text = request.form.get('edited_notes')
        return redirect(url_for('generate_flashcards', filename=filename, text=edited_text))
    raw_text = describe_image_with_gpt4(filepath)
    cleaned_text = clean_extracted_text(raw_text)
    return render_template('review.html', notes=cleaned_text, filename=filename)

@app.route('/generate/<filename>')
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
    return render_template('flashcards.html', flashcards=flashcards)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
