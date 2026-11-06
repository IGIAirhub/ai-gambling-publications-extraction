import pandas as pd
import argparse

parser = argparse.ArgumentParser(description='Stage 5: join the corpus with all three topic labels.')
parser.add_argument("--main", default="filtered_openalex_works.csv", help="corpus CSV (default: %(default)s)")
parser.add_argument("--gambling", default="gambling_topic_classified_papers.csv", help="gambling topic CSV (default: %(default)s)")
parser.add_argument("--ai", default="ai_topic_classified_papers.csv", help="AI topic CSV (default: %(default)s)")
parser.add_argument("--sports", default="sports_betting_classified_by_sport.csv", help="sport topic CSV (default: %(default)s)")
parser.add_argument("--output", default="master_classified_works.csv", help="merged output CSV (default: %(default)s)")
args = parser.parse_args()

# 1. Load all datasets
df_main = pd.read_csv(args.main)
df_gambling = pd.read_csv(args.gambling)
df_ai = pd.read_csv(args.ai)
df_sports = pd.read_csv(args.sports)

# 2. Sequential Merging
# We only select 'openalex_id' and the specific classification column from each 
# secondary file to keep the final CSV clean and avoid duplicate metadata columns.

# Merge Gambling Topics
df_combined = df_main.merge(
    df_gambling[['openalex_id', 'gambling_topic']], 
    on='openalex_id', 
    how='left'
)

# Merge AI Topics
df_combined = df_combined.merge(
    df_ai[['openalex_id', 'ai_topics']], 
    on='openalex_id', 
    how='left'
)

# Merge Sport Topics (from the new file)
df_combined = df_combined.merge(
    df_sports[['openalex_id', 'sport_topic']], 
    on='openalex_id', 
    how='left'
)

# 3. Apply Conditional Logic for the Sport Topic
# We define a "mask" for papers identified as Sports Betting
is_sports_betting = (df_combined['gambling_topic'] == 'Sports Betting')

# Case A: If it IS NOT Sports Betting, set sport_topic to 'Not Applicable'
df_combined.loc[~is_sports_betting, 'sport_topic'] = 'Not Applicable'

# Case B: If it IS Sports Betting but has no sport label (NaN), set to 'Unspecified'
df_combined.loc[is_sports_betting & df_combined['sport_topic'].isna(), 'sport_topic'] = 'Unspecified Sport'

# 4. Save the final merged file
df_combined.to_csv(args.output, index=False)

print(f"Final merger complete. Saved as '{args.output}'")
print(df_combined['sport_topic'].value_counts())