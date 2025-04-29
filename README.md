# Flashcards-AI
You can download the fine-tuned model (in safetensors format) here:  
[Download model from Google Drive](https://drive.google.com/drive/folders/1VpiVCcRd_sdNASXAAhqoZvGWDLWb07jF?usp=drive_link)

**Instructions:**
1. Download and unzip the model folder.
2. Place it in your `backend/` directory or any accessible path.
3. In your code, load it with:

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer

tokenizer = T5Tokenizer.from_pretrained('path/to/folder')
model = T5ForConditionalGeneration.from_pretrained('path/to/folder', trust_remote_code=True)
```

I started this project with the idea of building a tool to automate turning handwritten notes into flashcards using AI.
I initially tried using traditional OCR libraries like Tesseract (which produced poor results on messy handwriting) but my results were poor. So I decided to use the ChatGPT API directly to extract text from handwritten images, which gave far better flexibility and accuracy.

For flashcard generation, I found a trivia Q&A dataset on Kaggle. I wrote scripts to reformat this data into simulated handwritten notes and flashcard answers.
I trained a fine-tuned T5 model using PyTorch and HuggingFace Transformers — specifically, I ran 8 epochs with a learning rate of 5e-5, using a scheduler that linearly warmed up and decayed the learning rate.
Throughout training, I monitored the model's performance using BLEU scores and observed consistent improvements, achieving a final BLEU score around 62 with decreasing training loss across epochs.

On the backend, I built a Flask server to handle uploads and run flashcard generation. For the frontend, I used React with Vite and integrated Shadcn UI components to quickly build clean tables and user interfaces.
The frontend allows users to upload handwritten notes, view generated flashcards in a data table, and edit the content easily.
The design was first mocked up in Figma before implementation.

The final product is a full-stack application that takes handwritten notes and transforms them into polished flashcards using AI, with a clean, responsive frontend and a lightweight backend server.

Lessons Learned

Model Training: Monitoring BLEU scores across epochs helped gauge model improvements beyond just looking at training loss.

Fine-Tuning Strategy: Using a warm-up scheduler with the learning rate significantly helped model stability early in training.

Frontend Design: Using Shadcn's prebuilt components with React sped up development without sacrificing clean UI/UX.

Backend Simplification: Using the ChatGPT API directly for handwritten text extraction saved time compared to traditional OCR methods.

File Management: Proper .gitignore configuration is critical early on to prevent oversized files and cluttered repos.

Project Management: Planning the frontend with Figma first helped avoid constant design changes mid-coding.

Model Fine-Tuning Details
Dataset: Reformatted Trivia Q&A dataset from Kaggle

Model: T5-small fine-tuned using HuggingFace Transformers

Training:

8 epochs
Initial learning rate: 5e-5
Scheduler: Linear warm-up and decay
Optimizer: AdamW
Final BLEU Score: 62+