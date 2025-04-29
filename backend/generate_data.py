# flashcard_generation_pipeline.py

"""
This script does the following:
1. Loads an educational dataset (you can later plug in SQuAD or others)
2. Uses FLAN-T5 or GPT-2-large to auto-generate Q&A flashcards
3. Saves the results in a clean JSON format with "question" and "answer" fields
"""

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, GPT2LMHeadModel, GPT2Tokenizer
import torch
import json
import os
from datasets import load_dataset
from tqdm import tqdm
import re

# ========== CONFIG ==========
USE_FLAN_T5 = False  # Set to False to use GPT2-Large
MODEL_NAME = "google/flan-t5-base" if USE_FLAN_T5 else "openai-community/gpt2-large"
NUM_SAMPLES = 5  # How many notes to process from dataset
OUTPUT_PATH = "generated_flashcards.json"

# Few-shot examples for GPT2
FEW_SHOT_PROMPT = """
Note: Water boils at 100 degrees Celsius.
Q: At what temperature does water boil?
A: 100 degrees Celsius.

Note: The mitochondria is the powerhouse of the cell.
Q: What is the powerhouse of the cell?
A: The mitochondria.

"""

# ========== LOAD MODEL ==========
print(f"Loading model: {MODEL_NAME}")
if USE_FLAN_T5:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)
else:
    tokenizer = GPT2Tokenizer.from_pretrained(MODEL_NAME)
    model = GPT2LMHeadModel.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    model.config.pad_token_id = tokenizer.eos_token_id

# ========== LOAD DATA ==========
print("Loading dataset (SQuAD for demo)...")
dataset = load_dataset("squad", split="train[:1000]")
notes = [item["context"] for item in dataset.select(range(NUM_SAMPLES))]

# ========== DEBUG HELPER ==========
def test_extraction(output_string):
    print("\n🔍 Raw model output:")
    print(output_string)
    question, answer = None, None

    qa_match = re.search(r"Q[:\uFF1A]\s*(.*?)\s*A[:\uFF1A]\s*(.*)", output_string, re.IGNORECASE | re.DOTALL)
    if qa_match:
        question, answer = qa_match.group(1).strip(), qa_match.group(2).strip()
    else:
        lines = output_string.split("\n")
        q_candidates = [line.strip() for line in lines if line.strip().endswith("?")]
        a_candidates = [line.strip() for line in lines if not line.strip().endswith("?") and len(line.strip()) > 1]
        if q_candidates:
            question = q_candidates[0]
        if a_candidates:
            answer = a_candidates[0]

    print("\n🧪 Extraction result:")
    print("Question:", question)
    print("Answer:  ", answer)

# Uncomment below to test extraction manually
# test_extraction("Q: What is the capital of France?\nA: Paris.")

# ========== GENERATE FLASHCARDS ==========
flashcards = []
print("Generating flashcards...")

for note in tqdm(notes):
    if USE_FLAN_T5:
        prompt = (
            f"You are an AI assistant trained to create educational flashcards. "
            f"Read the note below and extract one factual question and its answer. "
            f"Your output must strictly follow this format:\n\n"
            f"Q: <question>\nA: <answer>\n\n"
            f"Note: {note}"
        )
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
        outputs = model.generate(**inputs, max_length=128)
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    else:
        prompt = FEW_SHOT_PROMPT + f"Note: {note}\nQ:"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)
        outputs = model.generate(
            **inputs,
            max_new_tokens=64,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7
        )
        result = tokenizer.decode(outputs[0], skip_special_tokens=True)
        result = result.split("Note:")[-1].strip()

    result = result.replace("Answer:", "A:").replace("Question:", "Q:")  # Normalize
    print("\n--- MODEL OUTPUT ---\n", result)  # Debug print

    # Extract Q and A using a fallback + heuristic-based method
    question, answer = None, None
    qa_match = re.search(r"Q[:\uFF1A]\s*(.*?)\s*A[:\uFF1A]\s*(.*)", result, re.IGNORECASE | re.DOTALL)
    if qa_match:
        question, answer = qa_match.group(1).strip(), qa_match.group(2).strip()
    else:
        lines = result.split("\n")
        q_candidates = [line for line in lines if line.strip().endswith("?")]
        a_candidates = [line for line in lines if not line.strip().endswith("?") and len(line.strip()) > 1]
        if q_candidates:
            question = q_candidates[0].strip()
        if a_candidates:
            answer = a_candidates[0].strip()

    if question and answer:
        flashcards.append({"input": note, "question": question, "answer": answer})
    else:
        print("⚠️ Extraction failed for:\n", result, "\n")
        flashcards.append({"input": note, "question": None, "answer": None, "raw_output": result})

# ========== SAVE OUTPUT ==========
print(f"Saving {len(flashcards)} flashcards to {OUTPUT_PATH}...")
with open(OUTPUT_PATH, "w") as f:
    json.dump(flashcards, f, indent=2, ensure_ascii=False)

print(" Done.")
