import pandas as pd
import ollama
import json
import argparse
import os
from tqdm import tqdm

# --- CONFIGURATION ---
parser = argparse.ArgumentParser(description='Stage 5: assign one gambling topic per paper (Ollama).')
parser.add_argument("--input", default="filtered_openalex_works.csv", help="corpus CSV (default: %(default)s)")
parser.add_argument("--output", default="topic_classified_gambling_papers.csv", help="output CSV; resumes if it exists (default: %(default)s)")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output
MODEL_NAME = "deepseek-r1:14b"

TOPICS = [
    "Sports Betting", "Poker", "Online Problem Gambling", "Casino Surveillance", 
    "Gambling Decision Making", "Gambling Website Detection", "Other"
]

system_prompt = f"""
You are an expert research assistant specializing in Gambling Studies and AI.
Your task is to classify academic publications into EXACTLY ONE of the following topics based on their title and abstract:

{', '.join(TOPICS)}

### Topic Definitions:
1. **Sports Betting**: Odds modeling, match outcome prediction, sportsbook markets, or athlete-specific wagering.
2. **Poker**: Game theory, poker AI/bots, strategy analysis, or professional poker play.
3. **Online Problem Gambling**: Detecting addiction, behavioral tracking of at-risk users, digital harm reduction, or clinical studies of online gamblers.
4. **Casino Surveillance**: Using AI/Computer Vision for cheating detection, floor monitoring, or security in physical casinos.
5. **Gambling Decision Making**: Cognitive biases, psychology of risk, neurological studies of gambling choice, or behavioral economics.
6. **Gambling Website Detection**: Web crawling, URL classification, or AI systems designed to identify and flag illegal or unlicensed gambling sites.
7. **Other**: Use this ONLY if the paper does not fit any above categories.

### Constraints:
- Respond ONLY with valid JSON: {{"topic": "Chosen Topic"}}
- The topic must match the list above exactly.
- Do not provide reasoning or preamble.
"""

def classify_text(text):
    if not text or pd.isna(text):
        return "Other"
    
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f"Text to classify: {text}"}
    ]
    
    try:
        response = ollama.chat(model=MODEL_NAME, messages=messages, format='json', options={'temperature': 0.0})
        result = json.loads(response['message']['content'])
        topic = result.get("topic", "Other")
        # Ensure the returned topic is in our allowed list
        return topic if topic in TOPICS else "Other"
    except Exception:
        return "Other"

def main():
    # Load CSV
    df = pd.read_csv(INPUT_FILE)
    
    # Check for existing progress
    if os.path.exists(OUTPUT_FILE):
        df_out = pd.read_csv(OUTPUT_FILE)
        # Create a mapping of what we've already processed
        processed_ids = set(df_out[df_out['gambling_topic'].notna()]['openalex_id'])
        print(f"Resuming: {len(processed_ids)} records already classified.")
    else:
        df_out = df.copy()
        df_out['gambling_topic'] = None
        processed_ids = set()

    # Iterate through rows
    for index, row in tqdm(df_out.iterrows(), total=len(df_out), desc="Classifying"):
        if row['openalex_id'] in processed_ids:
            continue
        
        # Use the combined title/abstract column
        topic = classify_text(row['title_abstract_combined'])
        df_out.at[index, 'gambling_topic'] = topic
        
        # Save every 10 rows to prevent data loss
        if index % 10 == 0:
            df_out.to_csv(OUTPUT_FILE, index=False)

    # Final Save
    df_out.to_csv(OUTPUT_FILE, index=False)
    print(f"Processing complete. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()