import json
import argparse
import os
import ollama
from tqdm import tqdm

# --- CONFIGURATION ---
parser = argparse.ArgumentParser(description='Stage 2: binary AI-related classifier (Ollama).')
parser.add_argument("--input", default="master_gambling_dataset.json", help="input JSON {id: {title, abstract}} (default: %(default)s)")
parser.add_argument("--output", default="master_ai_classification.json", help="output JSON {id: bool}; resumes if it exists (default: %(default)s)")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output
MODEL_NAME = "deepseek-r1:14b"

system_prompt = """ 
You are an expert research assistant specializing in the intersection of Gambling Studies and Computer Science. Your task is to classify academic publications as either AI-RELATED or NOT-AI-RELATED.
Classification Criteria: 
A publication is AI-RELATED if it meets either (or both) of the following:
AI as a Method: The study employs AI, this can include Machine Learning (ML), Natural Language Processing (NLP), Neural Networks, Computer Vision, Deep Learning, or Predictive Modeling.
This applies regardless of data source (survey data, financial records, etc.).
AI as a Subject: The study investigates AI (ML, language models, generative AI, etc.) as a topic of inquiry. This includes impact on the industry, ethics, policy, user perceptions, or literature reviews on AI.
NOT-AI-RELATED: The study does not use AI methods and does not focus on AI as a subject.
Respond ONLY in this JSON format: {"is_ai": boolean}
Do not provide any text outside of the JSON block.
"""

def classify_paper(title, abstract):
    paper_abstract = abstract if abstract else "No abstract provided."
    
    # Minimalist prompt for maximum speed
    messages = [
        {
            'role': 'system',
            'content': system_prompt
        },
        {
            'role': 'user', 
            'content': f"Title: {title}\nAbstract: {paper_abstract}"
        }
    ]
    
    try:
        # 'format: json' is key to keeping the output predictable
        response = ollama.chat(model=MODEL_NAME, messages=messages, format='json', options={'temperature': 0.0})
        result = json.loads(response['message']['content'])
        return result.get("is_ai")
    except Exception:
        return None # Mark as None so you can retry failed records later

def main():
    # Load source
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Load Checkpoint
    results = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            try:
                results = json.load(f)
                print(f"Resuming: {len(results)} records already done.")
            except: pass

    # Iterate
    for url, paper in tqdm(data.items(), desc="Processing"):
        if url in results:
            continue
            
        # Store just the boolean for maximum efficiency
        results[url] = classify_paper(paper['title'], paper['abstract'])
        
        # Save every 20 records to balance speed vs. safety
        if len(results) % 20 == 0:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(results, f)

    # Final Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()