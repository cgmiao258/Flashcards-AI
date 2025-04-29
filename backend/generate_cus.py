import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

# Device setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Load fine-tuned model and tokenizer
model_path = "finetuned_flan_t5_flashcards"
tokenizer = T5Tokenizer.from_pretrained(model_path)
model = T5ForConditionalGeneration.from_pretrained(model_path).to(device)

# Function to generate flashcard from a note
def generate_flashcard(note, max_length=50):
    # Tokenize and move to device
    inputs = tokenizer(note, return_tensors="pt", truncation=True, padding=True).to(device)
    
    # Generate output from model
    outputs = model.generate(**inputs, max_length=max_length)
    
    # Decode and return
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Example: Input your note string here
note_input = "the tower of london is actually located in china"

# Get the flashcard prediction
flashcard = generate_flashcard(note_input)

# Print result
print(" Generated Flashcard:")
print(flashcard)
