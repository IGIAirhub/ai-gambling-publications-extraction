import pandas as pd

# Load the dataset
file_name = 'gambling_topic_classified_papers.csv'
df = pd.read_csv(file_name)

def calculate_stats(df, year, topic):
    # Total publications in the given year
    total_year = len(df[df['publication_year'] == year])
    
    # Total publications for the specific topic in that year
    count_topic = len(df[(df['publication_year'] == year) & (df['gambling_topic'] == topic)])
    
    # Calculate percentage
    percentage = (count_topic / total_year * 100) if total_year > 0 else 0
    
    return total_year, count_topic, percentage

# Define the targets
years = [2016, 2017, 2018, 2019, 2025]
topics = ["Poker", "Sports Betting"]

print(f"{'Year':<6} | {'Topic':<15} | {'Topic Count':<12} | {'Total Year':<12} | {'Percentage'}")
print("-" * 65)

for year in years:
    for topic in topics:
        total, count, pct = calculate_stats(df, year, topic)
        print(f"{year:<6} | {topic:<15} | {count:<12} | {total:<12} | {pct:.2f}%")