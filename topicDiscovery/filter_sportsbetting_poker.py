import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Stage 4b (exploratory): drop already-resolved BERTopic topics before the next run.')
parser.add_argument("--input", default="paper_to_gambling_topic_firstrun.csv", help="previous run's document-topic CSV (default: %(default)s)")
parser.add_argument("--output", default="sports_betting_cluster_prep.csv", help="documents to re-cluster (default: %(default)s)")
args = parser.parse_args()

# 1. Load your current CSV
df = pd.read_csv(args.input)

# 2. Filter out rows where Topic is 0 or 1
# NOTE: these topic numbers come from the original first run. Topic numbers differ
# between runs, so replace them with the topics you want to drop from YOUR run.
# We use ~ to say "keep everything EXCEPT these"
filtered_df = df[~df['Topic'].isin([-1,1,2,3,4,5,6,7,8])]

# 3. Export to a new CSV
filtered_df.to_csv(args.output, index=False)

print(f"Done! Saved {len(filtered_df)} rows to '{args.output}'.")