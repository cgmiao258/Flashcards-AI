import torch
from torch.utils.data import DataLoader, Dataset, random_split
from torch.utils.tensorboard import SummaryWriter
from torch.optim import AdamW
from transformers import T5Tokenizer, T5ForConditionalGeneration, get_scheduler
import json
from tqdm import tqdm, trange
import evaluate  # Replaces deprecated load_metric

# FlashcardDataset Class
class FlashcardDataset(Dataset):
    def __init__(self, data_path, tokenizer_name, max_length=256):
        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        self.tokenizer = T5Tokenizer.from_pretrained(tokenizer_name)
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        note = item['note']
        qa = f"Q: {item['question']}\nA: {item['answer']}"
        encoding = self.tokenizer(note, padding="max_length", truncation=True, max_length=self.max_length, return_tensors="pt")
        target = self.tokenizer(qa, padding="max_length", truncation=True, max_length=self.max_length, return_tensors="pt")
        return {
            'input_ids': encoding['input_ids'].squeeze(),
            'attention_mask': encoding['attention_mask'].squeeze(),
            'labels': target['input_ids'].squeeze()
        }

# Settings
model_name = "google/flan-t5-base"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
epochs = 8
batch_size = 4
learning_rate = 5e-5
validation_split = 0.1

# Load tokenizer and model
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name).to(device)

# Load full dataset
full_dataset = FlashcardDataset("triviaqa_notes_generated.json", tokenizer_name=model_name)

# Split into train and val
val_size = int(len(full_dataset) * validation_split)
train_size = len(full_dataset) - val_size
train_dataset, val_dataset = random_split(full_dataset, [train_size, val_size])

train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=1)

# Optimizer
optimizer = AdamW(model.parameters(), lr=learning_rate)

# Learning rate scheduler
num_training_steps = epochs * len(train_loader)
lr_scheduler = get_scheduler(
    name="linear",
    optimizer=optimizer,
    num_warmup_steps=100,
    num_training_steps=num_training_steps,
)

# TensorBoard writer
writer = SummaryWriter("runs/flashcard_t5")

# Training loop
for epoch in trange(epochs, desc="Epochs"):
    print(f"\n🔁 Epoch {epoch+1}/{epochs}")
    model.train()
    total_loss = 0

    for step, batch in enumerate(tqdm(train_loader, desc="Training")):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)
        labels[labels == tokenizer.pad_token_id] = -100

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        lr_scheduler.step()

        total_loss += loss.item()
        writer.add_scalar("Loss/train", loss.item(), epoch * len(train_loader) + step)

    avg_loss = total_loss / len(train_loader)
    print(f"📉 Avg Training Loss: {avg_loss:.4f}")

    # Evaluation
    print("🔍 Evaluating...")
    model.eval()
    metric = evaluate.load("sacrebleu")
    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model.generate(input_ids=input_ids, attention_mask=attention_mask, max_length=50)
            preds = tokenizer.batch_decode(outputs, skip_special_tokens=True)
            refs = tokenizer.batch_decode(labels, skip_special_tokens=True)

            metric.add_batch(predictions=preds, references=[[r] for r in refs])

    score = metric.compute()["score"]
    print(f"📝 BLEU Score: {score:.2f}")
    writer.add_scalar("BLEU/score", score, epoch)

# Save final model
model.save_pretrained("finetuned_flan_t5_flashcards_v3")
tokenizer.save_pretrained("finetuned_flan_t5_flashcards_v3")
writer.close()
print("✅ Model and tokenizer saved.")
