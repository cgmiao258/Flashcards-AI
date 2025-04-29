import base64
import requests
import os
import openai
from PIL import Image
import cv2
import re

openai.api_key = os.getenv("OPENAI_API_KEY")  # or set directly: openai.api_key = "sk-..."

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        b64_image = base64.b64encode(img_file.read()).decode("utf-8")
    return b64_image

def describe_image_with_gpt4(image_path):
    base64_image = encode_image(image_path)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": (
                            "Please extract all readable text from this handwritten note image. Also, convert any mathematical symbols, variables, or notation into plain descriptive text (e.g., '∑' becomes 'summation', 'P(X|Y)' becomes 'probability of X given Y'). When giving your response, don't give any lead up like 'Sure, here is your answer...', only give the transcribed text" 
                        )},
                        {"type": "image_url", "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }},
                    ],
                }
            ],
            max_tokens=1024
        )

        content = response['choices'][0]['message']['content']
        return clean_extracted_text(content)

    except Exception as e:
        return f"❌ Error calling GPT-4 Vision: {e}"

import re

def clean_extracted_text(raw_text):
    drop_phrases = [
        "Sure, here is the extracted text",
        "Here is the extracted text",
        "Below is the extracted text",
        "This is what the note says",
        "The handwritten note contains the following text",
        "Generated text:",
        "Transcribed content:",
        "Sure, here's the extracted text and converted notation from the handwritten image:",
        "Sure! Here's the extracted text with mathematical notation converted to plain descriptive text:",
        "Certainly! Here's the transcription and conversion:",
        "Certainly! Here is the text extracted and converted:",
        "Sure, here’s the text extracted from the handwritten note:"

    ]
    
    # Normalize newlines and strip whitespace
    lines = raw_text.strip().splitlines()

    # Remove leading phrases
    for i, line in enumerate(lines):
        for phrase in drop_phrases:
            if phrase.lower() in line.lower():
                return "\n".join(lines[i + 1:]).strip()

    # Fallback: remove markdown/code fences or GPT-generated headers
    cleaned = re.sub(r"^```(?:\w+)?|```$", "", raw_text, flags=re.MULTILINE)
    cleaned = re.sub(r"(?i)^.*?(generated|transcribed|extracted) (text|content):", "", cleaned)

    return cleaned.strip()


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python convert_notes_to_text_gpt4.py <path_to_image>")
        sys.exit(1)

    image_path = sys.argv[1]
    print("🧠 Sending image to GPT-4 Vision...")
    result = describe_image_with_gpt4(image_path)

    output_path = os.path.join(os.path.dirname(os.path.abspath(image_path)), "ocr_output.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)
    print(f"✅ Text successfully saved to {output_path}")

    print("\n📄 GPT-4 Vision Output:\n" + "-" * 24)
    print(result)

if __name__ == "__main__":
    main()
