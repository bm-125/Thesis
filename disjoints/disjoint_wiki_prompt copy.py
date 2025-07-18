import csv
import google.generativeai as genai


# Replace with your actual Gemini API key
API_KEY = "AIzaSyDgrSB0HY5kzvNHY0akyZY7j-j5UWXcmVs"

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel(model_name="gemini-2.5-flash")

def query_model(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
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
                "You are a binary classification tool that receives two statements from Wikidata and "
                "classifies whether they are contradictory or not. Only answer yes or no. Do not repeat the statements.\n"
                f"Statement 1: {statement1.strip()}\n"
                f"Statement 2: {statement2.strip()}"
            )

            print(f"\n🔹 Prompt {i}:\n{prompt}")
            response = query_model(prompt)
            print(f"🔸 Output {i}: {response}")

            writer.writerow([i, statement1.strip(), statement2.strip(), response])

if __name__ == "__main__":
    input_file = "mixed_output.txt"
    output_file = "results_gemini_2_5.csv"
    process_file(input_file, output_file)

