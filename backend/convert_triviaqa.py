from datasets import load_dataset
import openai  # Only needed if using GPT-4 or GPT-3.5
import json
import time
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

NUM_SAMPLES = 1500  # How many QAs to use
BATCH_SIZE = 25     # Number of QAs per request
OUTPUT_FILE = "triviaqa_notes_generated.json"

# Load TriviaQA
dataset = load_dataset("trivia_qa", "unfiltered.nocontext", split="train[:2000]")

converted = []

print(" Generating notes from Q&A in batches...")

batch = []
for item in dataset:
    question = item.get("question", "").strip()
    answer = item.get("answer", {}).get("value", "").strip()

    if not question or not answer:
        continue

    batch.append((question, answer))

    if len(batch) == BATCH_SIZE:
        # Construct prompt with batched QAs
        prompt = "You are a helpful student taking notes from a teacher.\n\nHere are some Q&As. Write one realistic class note for each, labeled N1, N2, etc.:\n\n"
        for i, (q, a) in enumerate(batch, 1):
            prompt += f"Q{i}: {q}\nA{i}: {a}\n"
        prompt += "\nReturn one sentence note per Q&A as N1, N2, etc."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500
            )
            note_text = response.choices[0].message["content"].strip()

            # Extract each note
            for i, (q, a) in enumerate(batch, 1):
                label = f"N{i}:"
                note_line = next((line for line in note_text.splitlines() if line.startswith(label)), None)
                if note_line:
                    note = note_line[len(label):].strip()
                    converted.append({
                        "note": note,
                        "question": q,
                        "answer": a
                    })
                    print(f"✅ {len(converted)} / {NUM_SAMPLES}: {note}")
        except Exception as e:
            print(f" Failed on batch {len(converted)}: {e}")

        batch = []

    if len(converted) >= NUM_SAMPLES:
        break

# Save to file
print(f"💾 Saving to {OUTPUT_FILE}...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=2, ensure_ascii=False)

print(" Done.")
