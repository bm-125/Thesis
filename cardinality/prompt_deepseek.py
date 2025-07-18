import csv
from openai import OpenAI

# Configure the DeepSeek client
client = OpenAI(
    api_key="sk-0ae6483ee369445892d8af6cfd21d3b9",  # Replace with your actual DeepSeek API key
    base_url="https://api.deepseek.com"
)

def query_model(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
            model="deepseek-reasoner",  # or "deepseek-r1" if that's the correct model name
            messages=[
                {
                    "role": "system", 
                    "content": "You are a binary classification tool that receives two statements from Wikidata and classifies whether they are contradictory or not. Only answer yes or no. Do not repeat the statements."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.1,  # Lower temperature for more deterministic responses
            stream=False
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"❌ API error: {e}")
        return "error"

def process_file(input_path: str, output_path: str) -> None:
    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", encoding="utf-8", newline="") as outfile:

        reader = infile.readlines()
        writer = csv.writer(outfile)
        writer.writerow(["Prompt#", "Statement 1", "Statement 2", "Model Response"])

        for i, line in enumerate(reader, start=1):
            parts = line.strip().split(",", 1)
            if len(parts) != 2:
                print(f"⚠️ Skipping line {i}: expected 2 statements separated by a comma -> {line}")
                continue

            statement1, statement2 = parts
            prompt = (
                f"Statement 1: {statement1.strip()}\n"
                f"Statement 2: {statement2.strip()}"
            )

            print(f"\n🔹 Prompt {i}:\n{prompt}")
            response = query_model(prompt)
            print(f"🔸 Output {i}: {response}")

            writer.writerow([i, statement1.strip(), statement2.strip(), response])

if __name__ == "__main__":
    input_file = "mixed_output_cardinality.txt"
    output_file = "results_deepseekc.csv"
    process_file(input_file, output_file)