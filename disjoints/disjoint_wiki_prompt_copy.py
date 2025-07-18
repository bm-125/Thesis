import csv
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm

# Load chat model (with memory-efficient settings)
model_id = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"

print("🔄 Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)

print("🔄 Loading model...")
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    trust_remote_code=True,
    device_map="auto",
    torch_dtype=torch.float16
)

# Suppress pad_token_id warning
model.config.pad_token_id = tokenizer.eos_token_id

print("✅ Model and tokenizer loaded.\n")


def query_batch(prompts: list[str], max_new_tokens=50) -> list[str]:
    try:
        inputs = tokenizer(prompts, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(model.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)

        # Decode outputs
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)

        # Extract responses (strip original prompts from outputs)
        responses = []
        for full_out, prompt in zip(decoded, prompts):
            stripped = full_out[len(prompt):].strip()
            responses.append(stripped)

        return responses

    except Exception as e:
        print(f"❌ Batch error: {e}")
        return ["error"] * len(prompts)


def process_file(input_path: str, output_path: str, batch_size: int = 8) -> None:
    with open(input_path, "r", encoding="utf-8") as infile, \
         open(output_path, "w", encoding="utf-8", newline="") as outfile:

        reader = infile.readlines()
        writer = csv.writer(outfile)
        writer.writerow(["Prompt#", "Statement 1", "Statement 2", "Model Response"])

        prompts = []
        original_data = []

        for i, line in enumerate(tqdm(reader, desc="Reading prompts"), start=1):
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

            prompts.append(prompt)
            original_data.append((i, statement1.strip(), statement2.strip()))

            # Process batch when full
            if len(prompts) == batch_size:
                responses = query_batch(prompts)
                for (idx, stmt1, stmt2), response in zip(original_data, responses):
                    writer.writerow([idx, stmt1, stmt2, response])
                prompts = []
                original_data = []

        # Final batch if leftover
        if prompts:
            responses = query_batch(prompts)
            for (idx, stmt1, stmt2), response in zip(original_data, responses):
                writer.writerow([idx, stmt1, stmt2, response])


if __name__ == "__main__":
    input_file = "mixed_output.txt"
    output_file = "results_deepseek32b.csv"
    process_file(input_file, output_file, batch_size=8)



