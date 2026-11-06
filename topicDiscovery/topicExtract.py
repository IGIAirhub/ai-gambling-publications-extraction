import pandas as pd
import argparse
from bertopic import BERTopic
from bertopic.representation import OpenAI
import re
import openai
from sentence_transformers import SentenceTransformer


parser = argparse.ArgumentParser(description='Stage 4b (exploratory): BERTopic topic discovery, cluster names from a local LLM via Ollama.')
parser.add_argument("--input", default="sports_betting_cluster_prep.csv", help="CSV of documents to cluster (default: %(default)s)")
parser.add_argument("--text-column", default="Document", help="column holding the text (use title_abstract_combined for the first run on the corpus) (default: %(default)s)")
parser.add_argument("--topics-output", default="discovered_gambling_topics.csv", help="one row per discovered topic (default: %(default)s)")
parser.add_argument("--docs-output", default="paper_to_gambling_topic.csv", help="one row per document with its topic (default: %(default)s)")
args = parser.parse_args()

# 1. Load your consolidated data
df = pd.read_csv(args.input)
docs = df[args.text_column].astype(str).tolist()

# 2. Setup Local DeepSeek-R1 (Ollama Bridge)

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" # Still a placeholder
)

# We adjust the prompt to focus ONLY on the gambling context.
representation_model = OpenAI(
    client=client,
    model="qwen3:14b", 
    chat=True,
    prompt="""
    I have a cluster of sports betting research papers. 
    [DOCUMENTS]
    
    Keywords: [KEYWORDS]

    TASK: Provide a 1-4 word label that describes the SPORTS BETTING DOMAIN or CONTEXT of these papers.
    IGNORE the AI or machine learning methods used. Focus only on the 'what'.
    Return ONLY the label. Do not include <think> tags or explanations.
    """
)

embedding_model = SentenceTransformer("all-mpnet-base-v2")

# 3. Initialize BERTopic for Discovery
# min_topic_size=15 ensures we find meaningful groups in a 900-paper set.
topic_model = BERTopic(
    #representation_model=representation_model,
    embedding_model=embedding_model,
    # TUNE THIS: min_topic_size controls how coarse the clusters are. It was adjusted by hand
    # between runs until the clusters were interpretable; there is no single correct value.
    min_topic_size=10, 
    calculate_probabilities=True, # Needed for better outlier reduction later
    verbose=True
)

# 4. Fit the Model
print("Discovering gambling topics...")
topics, probs = topic_model.fit_transform(docs)

# 5. Outlier Reduction (The "No Paper Left Behind" step)
# This forces papers in Topic -1 into the most similar discovered topic.
# print("Reducing outliers...")
# new_topics = topic_model.reduce_outliers(docs, topics, strategy="c-tf-idf")
# topics = new_topics  # ✅ ensure downstream exports use reassigned topics
# topic_model.update_topics(docs, topics=new_topics)

topic_model.update_topics(
    docs,
    topics=topics,
    representation_model=representation_model
)


# 6. Clean LLM Labels (In case DeepSeek includes <think> tags)
def clean_label(label):
    return re.sub(r'<think>.*?</think>', '', label, flags=re.DOTALL).strip()

topic_info = topic_model.get_topic_info()
topic_info['Name'] = topic_info['Name'].apply(clean_label)

# 7. Export Standalone Results
print("Exporting results...")
topic_info.to_csv(args.topics_output, index=False)

# Document-level assignments for your review
doc_info = topic_model.get_document_info(docs)
doc_info['Name'] = doc_info['Name'].apply(clean_label)
doc_info.to_csv(args.docs_output, index=False)

# Interactive Map for your exploratory phase
topic_model.visualize_topics().write_html("gambling_domain_map.html")
topic_model.visualize_hierarchy().write_html("gambling_hierarchy.html")

print("Discovery Complete. View 'gambling_domain_map.html' to see the clusters.")