# Flashcards-AI
You can download the fine-tuned model (in safetensors format) here:  
👉 [Download model from Google Drive](https://drive.google.com/drive/folders/1VpiVCcRd_sdNASXAAhqoZvGWDLWb07jF?usp=drive_link)

**Instructions:**
1. Download and unzip the model folder.
2. Place it in your `backend/` directory or any accessible path.
3. In your code, load it with:

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer

tokenizer = T5Tokenizer.from_pretrained('path/to/folder')
model = T5ForConditionalGeneration.from_pretrained('path/to/folder', trust_remote_code=True)