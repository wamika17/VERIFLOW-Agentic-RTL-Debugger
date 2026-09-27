import os
import subprocess
from dotenv import load_dotenv
from openai import OpenAI

# Load OpenRouter API key
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise RuntimeError("OPENROUTER_API_KEY not found in .env")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)

# 1. Run Verilator
result = subprocess.run(
    ["verilator", "--lint-only", "top.sv", "alu.sv"],
    capture_output=True,
    text=True
)

verilator_output = result.stderr

print("=== VERILATOR DIAGNOSTICS ===")
print(verilator_output)

# 2. Send diagnostics to the AI
response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": (
                "You are an RTL lint analysis assistant. "
                "Analyze Verilator diagnostics and explain what each error means. "
                "Do not modify the code yet."
            )
        },
        {
            "role": "user",
            "content": (
                "Analyze these Verilator diagnostics:\n\n"
                + verilator_output
            )
        }
    ]
)

# 3. Print AI analysis
print("\n=== AI ANALYSIS ===")
print(response.choices[0].message.content)
