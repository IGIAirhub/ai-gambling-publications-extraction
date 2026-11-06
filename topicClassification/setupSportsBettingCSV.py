import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Stage 5: keep only papers labelled Sports Betting.')
parser.add_argument("--input", default="gambling_topic_classified_papers.csv", help="gambling topic classifier output CSV (default: %(default)s)")
parser.add_argument("--output", default="sports_betting_papers.csv", help="Sports Betting subset CSV (default: %(default)s)")
args = parser.parse_args()

# Load the dataset
file_name = args.input
df = pd.read_csv(file_name)

# Filter for rows where gambling_topic is "Sports Betting"
# We use .copy() to ensure the new dataframe is independent
sports_betting_df = df[df['gambling_topic'] == 'Sports Betting'].copy()

# Export the filtered data to a new CSV
output_name = args.output
sports_betting_df.to_csv(output_name, index=False)

print(f"Success! {len(sports_betting_df)} rows exported to {output_name}.")