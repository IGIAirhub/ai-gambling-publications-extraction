import json
import argparse
import os
import ollama
from tqdm import tqdm

# --- CONFIGURATION ---
parser = argparse.ArgumentParser(description='Stage 3: binary gambling-related classifier (Ollama).')
parser.add_argument("--input", default="master_gambling_dataset.json", help="input JSON {id: {title, abstract}} (default: %(default)s)")
parser.add_argument("--output", default="gambling_classifier_on_master.json", help="output JSON {id: bool}; resumes if it exists (default: %(default)s)")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output
MODEL_NAME = "deepseek-r1:14b"

system_prompt = """ 
You are an expert research assistant specializing in Gambling Studies.

Task: Classify an academic publication as either GAMBLING-RELATED or NOT-GAMBLING-RELATED using ONLY its title and abstract.

Decision Rule:
- Output GAMBLING-RELATED if gambling/betting/wagering (or gambling products, operators, regulation, harms, disorder, treatment, prevalence, consumer protection) is a topic, study domain, population, or application context.
- Output NOT-GAMBLING-RELATED if gambling terms are used only metaphorically, as a generic risk analogy, or as a purely mathematical/probability construct without real-world gambling context.

GAMBLING-RELATED includes research on:
1) Responsible / Safer Gambling & Harm Reduction:
   responsible gambling/gaming, safer gambling, harm minimization, prevention, interventions, self-exclusion, consumer protection
2) Gambling Disorder / Problem Gambling:
   problem gambling, pathological gambling, gambling disorder, compulsive gambling, PGSI, SOGS, DSM-5, treatment, relapse
3) Online / Mobile Gambling:
   online gambling, online betting, mobile betting, online casino, online poker/slots, gambling apps/websites/bookmakers
4) Sports Betting & Racing:
   sports betting/sportsbook/wagering/outcomes/predictions, betting markets/exchanges,odds, horse racing betting
5) Land-based gambling products & venues:
   casinos, casino patrons, slot machines/EGMs/VLTs/poker machines, table games, roulette/blackjack/craps/baccarat, poker
6) Policy / Regulation / Economics / Industry:
   gambling regulation, legislation, taxation, revenue, operators, market analysis, gambling participation/prevalence tied to gambling
7) Behavioral gambling research explicitly in gambling context:
   gambling cognitions, motivations, risky gambling behavior, gambler decision-making when explicitly tied to real gambling

NOT-GAMBLING-RELATED includes:
- metaphorical usage: “a gamble” in business/medicine/politics (“genetic gamble”, “investment gamble”, etc.)
- math/CS probability constructs without real-world gambling: gambler’s ruin, martingales, stochastic games
- decision theory/risk tasks not about gambling: Iowa Gambling Task (unless specifically used to study gambling disorder/gamblers)
- unrelated occurrences of matching terms
- loot boxes, skin gambling, or social casino games and does not concern real-world gambling

Output format:
Respond ONLY with valid JSON:
{"is_gambling": true/false}
Do not output any additional text.
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
        return result.get("is_gambling")
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