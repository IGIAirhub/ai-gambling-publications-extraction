import pandas as pd
import ollama
import json
import argparse
import os
from tqdm import tqdm

# --- CONFIGURATION ---
parser = argparse.ArgumentParser(description='Stage 5: assign one AI/ML topic per paper (Ollama).')
parser.add_argument("--input", default="filtered_openalex_works.csv", help="corpus CSV (default: %(default)s)")
parser.add_argument("--output", default="ai_topic_classified_papers.csv", help="output CSV; resumes if it exists (default: %(default)s)")
args = parser.parse_args()

INPUT_FILE = args.input
OUTPUT_FILE = args.output
MODEL_NAME = "deepseek-r1:14b"

AI_TOPICS = [
    "Machine Learning",
    "Computer Vision",
    "Pattern Recognition",
    "Natural Language Processing",
    "Knowledge based systems",
    "Generative AI",
    "Logic and reasoning",
    "Multi-agent systems",
    "Robots",
    "Other"
]

system_prompt = f"""
You are an expert research assistant specializing in Artificial Intelligence and Machine Learning.
Your task is to classify academic publications into EXACTLY ONE of the following AI/ML topics based on their title and abstract:

{', '.join(AI_TOPICS)}

### Topic Definitions:
1. **Machine Learning**: Supervised/unsupervised learning, deep learning methods, reinforcement learning, model training, evaluation, or general ML algorithms.
2. **Computer Vision**: Image/video understanding, object detection, segmentation, tracking, OCR, visual feature extraction.
3. **Pattern Recognition**: Feature extraction, classification methods, signal/image pattern analysis, statistical recognition, biometrics.
4. **Natural Language Processing**: Text mining, information extraction, embeddings, LLMs applied to text tasks, sentiment, topic modeling, IR.
5. **Knowledge based systems**: Expert systems, ontologies, knowledge graphs, rule-based inference, symbolic knowledge representation.
6. **Generative AI**: Generative models (GANs, diffusion, VAEs), text/image/audio generation, LLMs primarily used for generation.
7. **Logic and reasoning**: Formal logic, theorem proving, reasoning under uncertainty, SAT/SMT, planning, symbolic reasoning.
8. **Multi-agent systems**: Multi-agent learning, coordination, negotiation, game-theoretic agents, agent-based simulations.
9. **Robots**: Robotics, perception+control, motion planning, SLAM, manipulation, autonomous systems, embodied AI.
10. **Other**: Use this ONLY if the paper does not fit any above categories.

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
        response = ollama.chat(
            model=MODEL_NAME,
            messages=messages,
            format='json',
            options={'temperature': 0.0}
        )
        result = json.loads(response['message']['content'])
        topic = result.get("topic", "Other")
        return topic if topic in AI_TOPICS else "Other"
    except Exception:
        return "Other"

def main():
    # Load CSV
    df = pd.read_csv(INPUT_FILE)

    # Check for existing progress
    if os.path.exists(OUTPUT_FILE):
        df_out = pd.read_csv(OUTPUT_FILE)

        # Backward-compat: if old output used 'Topic' or 'gambling_topic', rename it once
        if 'Topic' in df_out.columns and 'ai_topics' not in df_out.columns:
            df_out = df_out.rename(columns={'Topic': 'ai_topics'})
        if 'gambling_topic' in df_out.columns and 'ai_topics' not in df_out.columns:
            df_out = df_out.rename(columns={'gambling_topic': 'ai_topics'})

        if 'ai_topics' not in df_out.columns:
            df_out['ai_topics'] = None

        processed_ids = set(df_out[df_out['ai_topics'].notna()]['openalex_id'])
        print(f"Resuming: {len(processed_ids)} records already classified.")
    else:
        df_out = df.copy()
        df_out['ai_topics'] = None
        processed_ids = set()

    # Iterate through rows
    for index, row in tqdm(df_out.iterrows(), total=len(df_out), desc="Classifying"):
        if row['openalex_id'] in processed_ids:
            continue

        # Use the combined title/abstract column
        topic = classify_text(row['title_abstract_combined'])
        df_out.at[index, 'ai_topics'] = topic

        # Save every 10 rows to prevent data loss
        if index % 10 == 0:
            df_out.to_csv(OUTPUT_FILE, index=False)

    # Final Save
    df_out.to_csv(OUTPUT_FILE, index=False)
    print(f"Processing complete. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
