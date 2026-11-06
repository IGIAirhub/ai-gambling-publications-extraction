import pandas as pd
import ollama
import json
import argparse
import os
import re
from tqdm import tqdm

# --- CONFIGURATION ---
parser = argparse.ArgumentParser(description='Stage 5: assign one sport per Sports Betting paper (Ollama).')
parser.add_argument("--input", default="sports_betting_papers.csv", help="Sports Betting subset CSV (default: %(default)s)")
parser.add_argument("--output", default="sports_betting_classified_by_sport.csv", help="output CSV; resumes if it exists (default: %(default)s)")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output
MODEL_NAME = "deepseek-r1:14b"

SPORTS_TOPICS = [
    "Basketball", "American Football", "Football/Soccer", 
    "Horse Racing", "Cricket", "Tennis", "Baseball", 
    "Combat Sport", "Ice Hockey", "Multi-sport", "Other"
]

system_prompt = f"""
You are an expert sports research analyst. Classify the publication into EXACTLY ONE category:
{', '.join(SPORTS_TOPICS)}

Rules:
1. **Multi-sport**: Only if 2+ specific sports are studied.
2. **Other**: General betting theory, math, or unlisted sports.
3. **Football/Soccer**: Association football/soccer only.

Output ONLY valid JSON: {{"sport_topic": "Chosen Sport"}}
"""

def classify_sport(text):
    if not text or pd.isna(text):
        return "Other"
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"Document: {text}"}
    ]
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=messages, options={'temperature': 0.0})
        raw_content = response['message']['content']
        
        # Strip DeepSeek <think> blocks
        clean_content = re.sub(r'<think>.*?</think>', '', raw_content, flags=re.DOTALL).strip()
        
        # Extract JSON object
        json_match = re.search(r'\{.*\}', clean_content, re.DOTALL)
        if json_match:
            result = json.loads(json_match.group())
            sport = result.get("sport_topic", "Other")
            # Ensure the model didn't hallucinate a category name
            return sport if sport in SPORTS_TOPICS else "Other"
        
        return "Other"
    except Exception:
        return "Other"

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    # Checkpoint handling: Resume if output file already exists
    if os.path.exists(OUTPUT_FILE):
        df_out = pd.read_csv(OUTPUT_FILE)
        print(f"Resuming: {df_out['sport_topic'].notna().sum()} records already classified.")
    else:
        df_out = pd.read_csv(INPUT_FILE)
        df_out['sport_topic'] = None

    # Iterate through the dataframe
    # Using 'title_abstract_combined' as the source text
    for index, row in tqdm(df_out.iterrows(), total=len(df_out), desc="Classifying"):
        if pd.notna(row['sport_topic']):
            continue
        
        text_to_process = row['title_abstract_combined']
        
        label = classify_sport(text_to_process)
        df_out.at[index, 'sport_topic'] = label
        
        # Save progress every 5 records
        if index % 5 == 0:
            df_out.to_csv(OUTPUT_FILE, index=False)

    # Final save
    df_out.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSuccess! Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()