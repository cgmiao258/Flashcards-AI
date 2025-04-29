import os
import sys
import openai

def read_notes(file_path):
    """
    Reads and returns the content of the text file containing your notes.
    """
    with open(file_path, 'r', encoding="utf-8") as file:
        return file.read()

def generate_flashcards(notes_text):
    """
    Sends the notes text to the ChatGPT API to generate flashcards.
    Returns the generated flashcards as text.
    """
    prompt = (
        "Please create a set of flashcards based on the following handwritten notes. "
        "For each flashcard, format it so that the question is on one side and the answer is on the other. "
        "Here are my notes:\n\n" + notes_text + "\n\n"
        "Format the flashcards in a clear, easy-to-read manner."
    )

    messages = [
        {"role": "system", "content": "You are an expert study assistant."},
        {"role": "user", "content": prompt}
    ]
    try:
        # Use the new interface to call the ChatCompletion endpoint.
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # You can change this to another model if desired.
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        # Extracting the flashcards from the response using dictionary keys:
        flashcards = response["choices"][0]["message"]["content"].strip()
        return flashcards
    except Exception as e:
        print(f"Error calling the OpenAI API: {e}")
        sys.exit(1)

def save_text_to_file(text, file_path):
    """
    Saves the provided text to the specified file, replacing it if it exists.
    """
    with open(file_path, 'w', encoding="utf-8") as file:
        file.write(text)
    print(f"Flashcards successfully saved to {file_path}")

def main():
    # Make sure the OpenAI API key is set in your environment.
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if openai.api_key is None:
        print("Error: The OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python generate_flashcards.py <notes_text_file>")
        sys.exit(1)

    notes_file = sys.argv[1]

    try:
        notes_text = read_notes(notes_file)
    except Exception as e:
        print(f"Error reading file {notes_file}: {e}")
        sys.exit(1)

    print("Generating flashcards from notes...")
    flashcards = generate_flashcards(notes_text)

    # Save flashcards to a file in the same directory as the notes text file.
    dir_name = os.path.dirname(os.path.abspath(notes_file))
    output_path = os.path.join(dir_name, "flashcards.txt")
    save_text_to_file(flashcards, output_path)
    
    print("\nGenerated Flashcards:\n---------------------")
    print(flashcards)

if __name__ == "__main__":
    main()
