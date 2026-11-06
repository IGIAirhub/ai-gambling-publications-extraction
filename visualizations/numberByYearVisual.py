import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the data
df = pd.read_csv('filtered_openalex_works.csv')

# 2. Aggregation: Group the data by year and count them
# value_counts() counts how many times each year appears
# sort_index() ensures the X-axis goes from oldest to newest (2010 -> 2025)
year_counts = df['publication_year'].value_counts().sort_index()

# 3. Create the Bar Chart
plt.bar(year_counts.index.astype(str), year_counts.values, color='skyblue', edgecolor='black')

# 4. Add Labels and Title
# plt.xlabel('Year of Publication', fontsize=12)
plt.ylabel('Number of AI publications in Gambling', fontsize=10)
plt.title('Number of AI publications in Gambling worldwide, 2010-2025', fontsize=12)

# 5. Clean up the look
plt.xticks(rotation=45) # Tilts the year labels so they don't overlap
plt.grid(axis='y', linestyle='--', alpha=0.7) # Adds soft horizontal lines
plt.tight_layout() # Ensures labels aren't cut off at the edges

# 6. Save the visual
plt.savefig('publications_by_year_other.png')
